module day10 (
    presses_p2,
    presses_p1,
    clear,
    clock,
    item_last,
    item_valid,
    load,
    ready,
    done_,
    part1_result,
    part2_result
);

    input [31:0] presses_p2;
    input [31:0] presses_p1;
    input clear;
    input clock;
    input item_last;
    input item_valid;
    input load;
    output ready;
    output done_;
    output [63:0] part1_result;
    output [63:0] part2_result;

    wire [63:0] _29;
    wire [31:0] _2;
    wire [31:0] _31;
    wire [63:0] _32;
    wire [63:0] _33;
    wire [63:0] _34;
    wire [63:0] _36;
    wire [63:0] _3;
    reg [63:0] _30;
    wire [31:0] _6;
    wire [63:0] _41;
    wire [63:0] _42;
    wire [63:0] _43;
    wire [63:0] _45;
    wire [63:0] _7;
    reg [63:0] _39;
    wire _23;
    wire _11;
    wire _13;
    wire vdd;
    wire _15;
    wire _17;
    wire _27;
    wire _46;
    wire _47;
    wire _19;
    wire _49;
    wire _20;
    reg _25;
    wire _26;
    assign _29 = 64'b0000000000000000000000000000000000000000000000000000000000000000;
    assign _2 = presses_p2;
    assign _31 = 32'b00000000000000000000000000000000;
    assign _32 = { _31,
                   _2 };
    assign _33 = _30 + _32;
    assign _34 = _27 ? _33 : _30;
    assign _36 = _19 ? _29 : _34;
    assign _3 = _36;
    always @(posedge _13) begin
        if (_11)
            _30 <= _29;
        else
            _30 <= _3;
    end
    assign _6 = presses_p1;
    assign _41 = { _31,
                   _6 };
    assign _42 = _39 + _41;
    assign _43 = _27 ? _42 : _39;
    assign _45 = _19 ? _29 : _43;
    assign _7 = _45;
    always @(posedge _13) begin
        if (_11)
            _39 <= _29;
        else
            _39 <= _7;
    end
    assign _23 = 1'b0;
    assign _11 = clear;
    assign _13 = clock;
    assign vdd = 1'b1;
    assign _15 = item_last;
    assign _17 = item_valid;
    assign _27 = _26 & _17;
    assign _46 = _27 & _15;
    assign _47 = _46 ? vdd : _25;
    assign _19 = load;
    assign _49 = _19 ? _23 : _47;
    assign _20 = _49;
    always @(posedge _13) begin
        if (_11)
            _25 <= _23;
        else
            _25 <= _20;
    end
    assign _26 = ~ _25;
    assign ready = _26;
    assign done_ = _25;
    assign part1_result = _39;
    assign part2_result = _30;

endmodule
