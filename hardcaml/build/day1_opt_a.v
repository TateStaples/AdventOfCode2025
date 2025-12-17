module day1_opt_a (
    magnitude,
    clear,
    clock,
    direction,
    instruction_valid,
    part1_result,
    part2_result,
    position
);

    input [15:0] magnitude;
    input clear;
    input clock;
    input direction;
    input instruction_valid;
    output [31:0] part1_result;
    output [31:0] part2_result;
    output [9:0] position;

    wire [31:0] _22;
    wire [49:0] _59;
    wire [17:0] _57;
    wire [49:0] _58;
    wire [99:0] _60;
    wire [67:0] _61;
    wire [99:0] _62;
    wire [17:0] _63;
    wire [15:0] _64;
    wire [17:0] _44;
    wire [17:0] _43;
    wire [17:0] _45;
    wire [17:0] _46;
    wire [49:0] _47;
    wire [99:0] _49;
    wire [67:0] _50;
    wire [99:0] _51;
    wire [17:0] _52;
    wire [17:0] _31;
    wire [17:0] _30;
    wire [17:0] _32;
    wire [49:0] _33;
    wire [99:0] _35;
    wire [67:0] _36;
    wire [99:0] _37;
    wire [17:0] _38;
    wire [17:0] _53;
    wire [15:0] _54;
    wire [15:0] _65;
    wire [15:0] _24;
    wire [31:0] _66;
    wire [31:0] _67;
    wire [31:0] _68;
    wire [31:0] _2;
    reg [31:0] _23;
    wire [31:0] _123;
    wire [9:0] _119;
    wire [17:0] _109;
    wire [49:0] _103;
    wire [99:0] _105;
    wire [67:0] _106;
    wire [99:0] _107;
    wire [17:0] _108;
    wire [35:0] _110;
    wire [17:0] _111;
    wire [17:0] _100;
    wire [17:0] _112;
    wire [9:0] _113;
    wire [49:0] _89;
    wire [99:0] _91;
    wire [67:0] _92;
    wire [99:0] _93;
    wire [17:0] _94;
    wire [35:0] _96;
    wire [17:0] _97;
    wire [49:0] _74;
    wire [99:0] _76;
    wire [67:0] _77;
    wire [99:0] _78;
    wire [17:0] _79;
    wire [35:0] _81;
    wire [17:0] _82;
    wire [15:0] _5;
    wire [1:0] _41;
    wire [17:0] _42;
    wire [17:0] _83;
    wire [9:0] _84;
    wire [7:0] _71;
    wire [17:0] _85;
    wire vdd;
    wire [9:0] _18;
    wire _7;
    wire _9;
    wire [9:0] _115;
    wire [9:0] _10;
    reg [9:0] _20;
    wire [17:0] _28;
    wire [17:0] _70;
    wire [17:0] _86;
    wire [17:0] _98;
    wire [9:0] _99;
    wire [9:0] _114;
    wire _120;
    wire _12;
    wire _121;
    wire [31:0] _124;
    wire [31:0] _125;
    wire _14;
    wire [31:0] _126;
    wire [31:0] _15;
    reg [31:0] _118;
    assign _22 = 32'b00000000000000000000000000000000;
    assign _59 = 50'b00000000000000000000000010100011110101110000101001;
    assign _57 = _28 + _42;
    assign _58 = { _22,
                   _57 };
    assign _60 = _58 * _59;
    assign _61 = _60[99:32];
    assign _62 = { _22,
                   _61 };
    assign _63 = _62[17:0];
    assign _64 = _63[15:0];
    assign _44 = 18'b000000000000000001;
    assign _43 = _28 - _42;
    assign _45 = _43 - _44;
    assign _46 = _45 + _31;
    assign _47 = { _22,
                   _46 };
    assign _49 = _47 * _59;
    assign _50 = _49[99:32];
    assign _51 = { _22,
                   _50 };
    assign _52 = _51[17:0];
    assign _31 = 18'b010000000001000000;
    assign _30 = _28 - _44;
    assign _32 = _30 + _31;
    assign _33 = { _22,
                   _32 };
    assign _35 = _33 * _59;
    assign _36 = _35[99:32];
    assign _37 = { _22,
                   _36 };
    assign _38 = _37[17:0];
    assign _53 = _38 - _52;
    assign _54 = _53[15:0];
    assign _65 = _12 ? _64 : _54;
    assign _24 = 16'b0000000000000000;
    assign _66 = { _24,
                   _65 };
    assign _67 = _23 + _66;
    assign _68 = _14 ? _67 : _23;
    assign _2 = _68;
    always @(posedge _9) begin
        if (_7)
            _23 <= _22;
        else
            _23 <= _2;
    end
    assign _123 = 32'b00000000000000000000000000000001;
    assign _119 = 10'b0000000000;
    assign _109 = 18'b000000000001100100;
    assign _103 = { _22,
                    _100 };
    assign _105 = _103 * _59;
    assign _106 = _105[99:32];
    assign _107 = { _22,
                    _106 };
    assign _108 = _107[17:0];
    assign _110 = _108 * _109;
    assign _111 = _110[17:0];
    assign _100 = _28 + _42;
    assign _112 = _100 - _111;
    assign _113 = _112[9:0];
    assign _89 = { _22,
                   _86 };
    assign _91 = _89 * _59;
    assign _92 = _91[99:32];
    assign _93 = { _22,
                   _92 };
    assign _94 = _93[17:0];
    assign _96 = _94 * _109;
    assign _97 = _96[17:0];
    assign _74 = { _22,
                   _42 };
    assign _76 = _74 * _59;
    assign _77 = _76[99:32];
    assign _78 = { _22,
                   _77 };
    assign _79 = _78[17:0];
    assign _81 = _79 * _109;
    assign _82 = _81[17:0];
    assign _5 = magnitude;
    assign _41 = 2'b00;
    assign _42 = { _41,
                   _5 };
    assign _83 = _42 - _82;
    assign _84 = _83[9:0];
    assign _71 = 8'b00000000;
    assign _85 = { _71,
                   _84 };
    assign vdd = 1'b1;
    assign _18 = 10'b0000110010;
    assign _7 = clear;
    assign _9 = clock;
    assign _115 = _14 ? _114 : _20;
    assign _10 = _115;
    always @(posedge _9) begin
        if (_7)
            _20 <= _18;
        else
            _20 <= _10;
    end
    assign _28 = { _71,
                   _20 };
    assign _70 = _28 + _109;
    assign _86 = _70 - _85;
    assign _98 = _86 - _97;
    assign _99 = _98[9:0];
    assign _114 = _12 ? _113 : _99;
    assign _120 = _114 == _119;
    assign _12 = direction;
    assign _121 = _12 & _120;
    assign _124 = _121 ? _123 : _22;
    assign _125 = _118 + _124;
    assign _14 = instruction_valid;
    assign _126 = _14 ? _125 : _118;
    assign _15 = _126;
    always @(posedge _9) begin
        if (_7)
            _118 <= _22;
        else
            _118 <= _15;
    end
    assign part1_result = _118;
    assign part2_result = _23;
    assign position = _20;

endmodule
