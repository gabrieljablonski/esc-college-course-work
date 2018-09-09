// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

	@R0
	D=M
	@mult1 // Multiplicand
	M=D
	
	@R1
	D=M
	@mult2 // Multiplier
	M=D
	
	@R2    // Product
	M=0
	
	@i     // Counting variable
	M=0
	
(LOOP)
	@i
	D=M
	@mult2
	D=D-M
	@END
	D; JEQ // if (i-mult2 == 0) goto END;
	
	@mult1
	D=M
	@R2
	M=M+D  // Add mult1 to R2
	
	@i     // Increase count
	M=M+1
	
	@LOOP
	0; JMP

(END)
	@END
	0; JMP
