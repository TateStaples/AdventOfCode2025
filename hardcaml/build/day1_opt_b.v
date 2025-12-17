module day1_opt_b (
    magnitude,
    direction,
    clear,
    clock,
    instruction_valid,
    part1_result,
    part2_result,
    position
);

    input [15:0] magnitude;
    input direction;
    input clear;
    input clock;
    input instruction_valid;
    output [31:0] part1_result;
    output [31:0] part2_result;
    output [9:0] position;

    wire [31:0] _25;
    wire [49:0] _62;
    wire [17:0] _60;
    wire [49:0] _61;
    wire [99:0] _63;
    wire [67:0] _64;
    wire [99:0] _65;
    wire [17:0] _66;
    wire [15:0] _67;
    wire [17:0] _47;
    wire [17:0] _46;
    wire [17:0] _48;
    wire [17:0] _49;
    wire [49:0] _50;
    wire [99:0] _52;
    wire [67:0] _53;
    wire [99:0] _54;
    wire [17:0] _55;
    wire [17:0] _34;
    wire [17:0] _33;
    wire [17:0] _35;
    wire [49:0] _36;
    wire [99:0] _38;
    wire [67:0] _39;
    wire [99:0] _40;
    wire [17:0] _41;
    wire [17:0] _56;
    wire [15:0] _57;
    wire [15:0] _68;
    wire [15:0] _27;
    wire [31:0] _69;
    reg [31:0] _72;
    wire [31:0] _73;
    wire [31:0] _74;
    wire [31:0] _2;
    reg [31:0] _26;
    wire [31:0] _131;
    wire [9:0] _128;
    wire [17:0] _115;
    wire [49:0] _109;
    wire [99:0] _111;
    wire [67:0] _112;
    wire [99:0] _113;
    wire [17:0] _114;
    wire [35:0] _116;
    wire [17:0] _117;
    wire [17:0] _106;
    wire [17:0] _118;
    wire [9:0] _119;
    wire [49:0] _95;
    wire [99:0] _97;
    wire [67:0] _98;
    wire [99:0] _99;
    wire [17:0] _100;
    wire [35:0] _102;
    wire [17:0] _103;
    wire [49:0] _80;
    wire [99:0] _82;
    wire [67:0] _83;
    wire [99:0] _84;
    wire [17:0] _85;
    wire [35:0] _87;
    wire [17:0] _88;
    wire [15:0] _5;
    wire [1:0] _44;
    wire [17:0] _45;
    wire [17:0] _89;
    wire [9:0] _90;
    wire [7:0] _77;
    wire [17:0] _91;
    wire [9:0] _18;
    reg [9:0] _123;
    wire [9:0] _124;
    wire [9:0] _6;
    reg [9:0] _20;
    wire [17:0] _31;
    wire [17:0] _76;
    wire [17:0] _92;
    wire [17:0] _104;
    wire [9:0] _105;
    wire _8;
    wire [9:0] _120;
    wire _129;
    wire [31:0] _132;
    reg [31:0] _135;
    wire [31:0] _136;
    wire vdd;
    wire _22;
    wire _10;
    wire _12;
    wire _14;
    reg _23;
    wire [31:0] _137;
    wire [31:0] _15;
    reg [31:0] _127;
    assign _25 = 32'b00000000000000000000000000000000;
    assign _62 = 50'b00000000000000000000000010100011110101110000101001;
    assign _60 = _31 + _45;
    assign _61 = { _25,
                   _60 };
    assign _63 = _61 * _62;
    assign _64 = _63[99:32];
    assign _65 = { _25,
                   _64 };
    assign _66 = _65[17:0];
    assign _67 = _66[15:0];
    assign _47 = 18'b000000000000000001;
    assign _46 = _31 - _45;
    assign _48 = _46 - _47;
    assign _49 = _48 + _34;
    assign _50 = { _25,
                   _49 };
    assign _52 = _50 * _62;
    assign _53 = _52[99:32];
    assign _54 = { _25,
                   _53 };
    assign _55 = _54[17:0];
    assign _34 = 18'b010000000001000000;
    assign _33 = _31 - _47;
    assign _35 = _33 + _34;
    assign _36 = { _25,
                   _35 };
    assign _38 = _36 * _62;
    assign _39 = _38[99:32];
    assign _40 = { _25,
                   _39 };
    assign _41 = _40[17:0];
    assign _56 = _41 - _55;
    assign _57 = _56[15:0];
    assign _68 = _8 ? _67 : _57;
    assign _27 = 16'b0000000000000000;
    assign _69 = { _27,
                   _68 };
    always @(posedge _12) begin
        if (_10)
            _72 <= _25;
        else
            if (_14)
                _72 <= _69;
    end
    assign _73 = _26 + _72;
    assign _74 = _23 ? _73 : _26;
    assign _2 = _74;
    always @(posedge _12) begin
        if (_10)
            _26 <= _25;
        else
            _26 <= _2;
    end
    assign _131 = 32'b00000000000000000000000000000001;
    assign _128 = 10'b0000000000;
    assign _115 = 18'b000000000001100100;
    assign _109 = { _25,
                    _106 };
    assign _111 = _109 * _62;
    assign _112 = _111[99:32];
    assign _113 = { _25,
                    _112 };
    assign _114 = _113[17:0];
    assign _116 = _114 * _115;
    assign _117 = _116[17:0];
    assign _106 = _31 + _45;
    assign _118 = _106 - _117;
    assign _119 = _118[9:0];
    assign _95 = { _25,
                   _92 };
    assign _97 = _95 * _62;
    assign _98 = _97[99:32];
    assign _99 = { _25,
                   _98 };
    assign _100 = _99[17:0];
    assign _102 = _100 * _115;
    assign _103 = _102[17:0];
    assign _80 = { _25,
                   _45 };
    assign _82 = _80 * _62;
    assign _83 = _82[99:32];
    assign _84 = { _25,
                   _83 };
    assign _85 = _84[17:0];
    assign _87 = _85 * _115;
    assign _88 = _87[17:0];
    assign _5 = magnitude;
    assign _44 = 2'b00;
    assign _45 = { _44,
                   _5 };
    assign _89 = _45 - _88;
    assign _90 = _89[9:0];
    assign _77 = 8'b00000000;
    assign _91 = { _77,
                   _90 };
    assign _18 = 10'b0000110010;
    always @(posedge _12) begin
        if (_10)
            _123 <= _128;
        else
            if (_14)
                _123 <= _120;
    end
    assign _124 = _23 ? _123 : _20;
    assign _6 = _124;
    always @(posedge _12) begin
        if (_10)
            _20 <= _18;
        else
            _20 <= _6;
    end
    assign _31 = { _77,
                   _20 };
    assign _76 = _31 + _115;
    assign _92 = _76 - _91;
    assign _104 = _92 - _103;
    assign _105 = _104[9:0];
    assign _8 = direction;
    assign _120 = _8 ? _119 : _105;
    assign _129 = _120 == _128;
    assign _132 = _129 ? _131 : _25;
    always @(posedge _12) begin
        if (_10)
            _135 <= _25;
        else
            if (_14)
                _135 <= _132;
    end
    assign _136 = _127 + _135;
    assign vdd = 1'b1;
    assign _22 = 1'b0;
    assign _10 = clear;
    assign _12 = clock;
    assign _14 = instruction_valid;
    always @(posedge _12) begin
        if (_10)
            _23 <= _22;
        else
            _23 <= _14;
    end
    assign _137 = _23 ? _136 : _127;
    assign _15 = _137;
    always @(posedge _12) begin
        if (_10)
            _127 <= _25;
        else
            _127 <= _15;
    end
    assign part1_result = _127;
    assign part2_result = _26;
    assign position = _20;

endmodule
