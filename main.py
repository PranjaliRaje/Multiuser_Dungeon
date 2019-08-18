#!/usr/bin/env python


import time
import json
from mudserver import MudServer


# imported from rooms.json, defines rooms
with open('rooms.json', 'r') as f:
    rooms = json.load(f)
# stores the players in the game
players = {}
# start the server
mud = MudServer()

# main game infinite loop
while True:
 
    # calling update for uptodate information
    mud.update()

    # go through any newly connected players
    for id in mud.get_new_players():

        # adding  the new player to the dictionary with their name and room empty
        players[id] = {
            "name": None,
            "room": None,
        }

        # ask the new player for their name
        mud.send_message(id, "What is your name?")

    # go through any recently disconnected players
    for id in mud.get_disconnected_players():
        
        # if player not present continue the loop
        if id not in players:
            continue

        # go through all the players in the game
        for pid, pl in players.items():
            # send each player a message to tell them about the diconnected player
            mud.send_message(pid, "{} quit the game".format(players[id]["name"]))

        # remove the player's entry 
        del(players[id])

    # go through any new commands sent from players
    for id, command, params in mud.get_commands():

        # if player not present continue the loop
        if id not in players:
            continue

        # Take player's name and make hime enter the default room
        if players[id]["name"] is None:
            players[id]["name"] = command
            players[id]["room"] = "1"


            playershere=[]
            rm = rooms[players[id]["room"]]

            for pid, pl in players.items():
                # send each player a message to tell them about the new player
                mud.send_message(pid, "{} entered the game".format( players[id]["name"]))
                
                # collecting info about players in the same rrom
                if players[pid]["room"] == players[id]["room"]:
                    if players[pid]["name"] is not None:                      
                        # add their name to the list
                        playershere.append(players[pid]["name"])
                        
            # send the new player a welcome message
            mud.send_message(id, "Welcome to the game, {}. ".format(players[id]["name"]) + "Type 'help' for a list of commands.")

            # send the new player the description of their current room
            mud.send_message(id, rooms[players[id]["room"]]["description"])
            
            # send the new player a message containing list of players in the room
            mud.send_message(id, "Players here: {}".format(", ".join(playershere)))

            # send player a message containing the list of exits from this room
            mud.send_message(id, "Exits are: {}".format(", ".join(rm["exits"])))


        # 'help' command
        elif command == "help":

            mud.send_message(id, "Commands:")
            mud.send_message(id, "  say <message>         - Say something to players in your room.")
            mud.send_message(id, "  tell <name> <message> - Message someone privately ")
            mud.send_message(id, "  yell <message>        - Yell something to everyone in the game ")
            mud.send_message(id, "  <direction>           - Move in adjacent room through possible exits. Eg- north/south/east/west/up/down")
        # 'say' command
        elif command == "say":

            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # send them a message telling them what the player said
                    mud.send_message(pid, "{} says: {}".format(players[id]["name"], params))
        
        elif command == "tell":
            player_name, message = params.split(" ",1)    
            # go through every player in the game
            for pid, pl in players.items():
                # if they're the same person player wants to send message to tell them what player said
                if players[pid]["name"] == player_name:
                    mud.send_message(pid, "{} tells: {}".format(players[id]["name"], message))
        
        elif command == "yell":
                
            # go through every player in the game
            for pid, pl in players.items():
                # tell everyone what player said
                mud.send_message(pid, "{} yells: {}".format(players[id]["name"], params))
                    
                    
        
        elif command in ["north","east","south","west","up","down"]:


            # store the player's current room
            rm = rooms[players[id]["room"]]

            # if the specified exit is found in the room's exits list
            if command in rm["exits"]:

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same room and isn't the player sending the command
                    if players[pid]["room"] == players[id]["room"] and pid != id:
                        # send them a message telling them that the player left the room
                        mud.send_message(pid, "{} left via exit '{}'".format(players[id]["name"], command))

                # update the player's current room to the one the exit leads to
                players[id]["room"] = rm["exits"][command]
                rm = rooms[players[id]["room"]]

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same (new) room and isn't the player sending the command
                    if players[pid]["room"] == players[id]["room"] and pid != id:
                        # send them a message telling them that the player entered the room
                        mud.send_message(pid,"{} arrived via exit '{}'".format(players[id]["name"], command))

                # send the player a message telling them where they are now
                mud.send_message(id, "You arrive at '{}'".format(rooms[players[id]["room"]]["name"]))
                

                playershere = []
                # go through every player in the game
                for pid, pl in players.items():
                    # if they're in the same room as the player
                    if players[pid]["room"] == players[id]["room"]:
                        if players[pid]["name"] is not None:
                            
                            # add their name to the list
                            playershere.append(players[pid]["name"])
            
                # send player a message containing the list of players in the room
                mud.send_message(id, "Players here: {}".format(", ".join(playershere)))
            
                # send player a message containing the list of exits from this room
                mud.send_message(id, "Exits are: {}".format(", ".join(rm["exits"])))
            # the specified exit wasn't found in the current room
            else:
                mud.send_message(id, "exit blocked for'{}'".format(command))

        # some other, unrecognised command
        else:
            # send back an 'unknown command' message
            mud.send_message(id, "Unknown command '{}'".format(command))
