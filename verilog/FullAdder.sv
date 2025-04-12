module FullAdder(
    input  logic a,
    input  logic b,
    input  logic cin,
    output logic sum,
    output logic cout
);

    assign sum = a ^ (b ^ cin); // Sum is the XOR of a, b, and cin
    assign cout = ((a & b) | (b & cin)) | (a & cin); // Cout is the OR of the AND of a and b, the AND of b and cin, and the AND of a and cin

    logic d;
    assign d = sum ~& sum;

endmodule
