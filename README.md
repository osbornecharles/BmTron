Paradigms Final Project - Gabe vs. Doge Tron
===========================================

Names: Mimi Chen and Charlie Osborne

Description
---------------
Our game is a 2-Player Gabe vs. Doge version of Tron. Player 1 is the host 
player, and Player 2 is the client player that joins the game started by 
Player 1.  The objective of the game is to not die by not running into the 
wall or either player's trail. 

**Characters**

The characters for the game are Doge and Gabe. In the game, Player 1 is "gabe" 
(white dog that borks). Player 2 is "doge" ("project much long, many pains").


**Multiple Scenes**

Our game has 4 scenes: 

	1. Loading Scene: waits for the other player to connect

	2. Title Scene: displays the game title with cute pictures. The title scene
	waits until both players are ready before starting the game

	3. Game Scene: actual game

	4. End Scene: displays who the winner is

Tutorial
----------------
1. Start Player 1. Player 1's window is the "loadScene" that waits for P2
to connect.

		$ python3 p1.py

2. Start Player 2.

		$ python3 p2.py 

3. Once the command and data connections have been established, P1 and P2
will be directed to the "titleScene" where P1 and P2 need to click the 
button "Start" to begin playing

4. P1 (gabe) begins on the left side of the game window and moves right. 
P2 (doge) begins on the right side of the game window and moves left. P1 
and P2 can control their character with UP, DOWN, LEFT, and RIGHT arrows.

5. If P1 or P2 crashes into a wall or trail, they die and the other player 
wins. 
