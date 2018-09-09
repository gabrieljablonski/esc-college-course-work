// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(RESET) // Reset pointer to start of screen map
	@SCREEN
	D=A
	@cur_screen_word // Pointer to current word being operated on
	M=D

(LOOP)	
	@KBD
	D=M
	
	@FILL // if any key is pressed (M[KBD] > 0), then fill word
	D; JGT
	
	@BLANK // else, blank word
	0; JMP
	
(FILL)
	@cur_screen_word
	A=M
	M=-1
	
	@CHECK
	0; JMP
	
(BLANK)
	@cur_screen_word
	A=M
	M=0
	
	@CHECK
	0; JMP
	
(CHECK) // Check if reached end of screen map
	@cur_screen_word
	MD=M+1
	@KBD
	D=D-A
	
	@RESET // if M[cur_screen_word] == KBD, reset to start of screen map
	D; JEQ
	
	@LOOP  // else, continue filling/blanking
	0; JMP
	