
module cnt_abstract_eg (input logic clk,
			input logic rst_n,
			output logic A,
			output logic B,
			output logic C,
			output logic D
			);

	logic [31:0] cntr; //Giant counter
	
	wire cntr_full = &cntr;

	always @ ( posedge clk or negedge rst_n)
		begin
			if ( ~rst_n)
				begin
					cntr <= 0;
					A <= 1'b0;
					B <= 1'b0;
					C <= 1'b0;
					D <= 1'b0;
				end
			else
				begin
					cntr <= cntr + 1;
					
					if ( cntr == ((2**23) - 19346 ) )
						A <= 1'b1;

					if ( cntr == ((2**28) - 28311 ) )
						B <= 1'b1;
		
				end
		end

endmodule
