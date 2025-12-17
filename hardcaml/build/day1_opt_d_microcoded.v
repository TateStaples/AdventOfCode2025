module day1_opt_d_microcoded (
    instruction_mag,
    instruction_valid,
    instruction_dir,
    clear,
    clock,
    ready,
    part1_result,
    part2_result,
    position
);

    input [15:0] instruction_mag;
    input instruction_valid;
    input instruction_dir;
    input clear;
    input clock;
    output ready;
    output [31:0] part1_result;
    output [31:0] part2_result;
    output [9:0] position;

    wire [31:0] _108;
    wire [17:0] _51;
    wire [17:0] _71;
    wire [17:0] _2;
    reg [17:0] _52;
    wire [17:0] _78;
    wire [17:0] _3;
    reg [17:0] _77;
    wire [16:0] _56;
    wire [17:0] _69;
    wire [17:0] _98;
    wire [17:0] _100;
    wire [17:0] _4;
    reg [17:0] _55;
    wire [17:0] _70;
    wire [17:0] _104;
    wire [17:0] _5;
    reg [17:0] _103;
    wire [17:0] _111;
    wire [17:0] _112;
    wire [13:0] _110;
    wire [31:0] _113;
    wire [31:0] _114;
    wire [31:0] _115;
    wire [31:0] _6;
    reg [31:0] _109;
    wire [31:0] _176;
    wire [9:0] _172;
    wire [17:0] _125;
    wire [17:0] _66;
    wire [1:0] _160;
    wire [17:0] _161;
    wire [15:0] _9;
    wire [17:0] _120;
    wire [17:0] _121;
    wire [17:0] _10;
    reg [17:0] _118;
    wire [7:0] _155;
    wire [17:0] _156;
    wire [17:0] _157;
    wire [17:0] _151;
    wire [17:0] _153;
    wire [17:0] _154;
    wire [17:0] _158;
    wire [17:0] _147;
    wire [17:0] _146;
    wire [17:0] _148;
    wire [6:0] _123;
    wire [6:0] _128;
    wire [6:0] _129;
    wire [6:0] _11;
    reg [6:0] _124;
    wire [10:0] _142;
    wire [17:0] _143;
    wire [9:0] _32;
    wire [9:0] _133;
    wire [9:0] _12;
    reg [9:0] _34;
    wire [17:0] _139;
    wire [17:0] _141;
    wire [17:0] _144;
    wire [17:0] _149;
    wire [17:0] _159;
    wire [17:0] _162;
    wire [16:0] _134;
    wire [17:0] _136;
    wire [17:0] _137;
    wire [17:0] _163;
    wire [17:0] _13;
    reg [17:0] _63;
    wire _64;
    wire [16:0] _60;
    wire [17:0] _65;
    wire _67;
    wire _68;
    wire [17:0] _126;
    wire [17:0] _164;
    wire [17:0] _166;
    wire [17:0] _14;
    reg [17:0] _59;
    wire [17:0] _127;
    wire [9:0] _167;
    wire [9:0] _168;
    wire [9:0] _15;
    reg [9:0] _132;
    wire _173;
    wire _174;
    wire [31:0] _177;
    wire [31:0] _178;
    wire [31:0] _179;
    wire [31:0] _16;
    reg [31:0] _171;
    wire [2:0] _79;
    wire [2:0] _201;
    wire [2:0] _199;
    wire [2:0] _197;
    wire [2:0] _195;
    wire [2:0] _193;
    wire _106;
    wire [2:0] _190;
    wire _73;
    wire _74;
    wire [2:0] _192;
    wire [2:0] _194;
    wire [2:0] _196;
    wire _188;
    wire [2:0] _198;
    wire [2:0] _200;
    wire _19;
    wire _36;
    wire gnd;
    wire _186;
    wire _95;
    wire _96;
    wire _21;
    wire _180;
    wire _22;
    reg _90;
    wire _91;
    wire _48;
    wire _49;
    wire _92;
    wire _85;
    wire [4:0] _41;
    wire vdd;
    wire [4:0] _39;
    wire _24;
    wire _26;
    wire [4:0] _184;
    wire [4:0] _182;
    wire [4:0] _183;
    wire [4:0] _185;
    wire [4:0] _27;
    reg [4:0] _40;
    wire _42;
    wire _43;
    wire _86;
    wire _87;
    wire _93;
    wire _97;
    wire _187;
    wire _28;
    reg _37;
    wire _81;
    wire _82;
    wire _83;
    wire [2:0] _202;
    wire [2:0] _29;
    reg [2:0] _46;
    wire _80;
    assign _108 = 32'b00000000000000000000000000000000;
    assign _51 = 18'b000000000000000000;
    assign _71 = _49 ? _70 : _52;
    assign _2 = _71;
    always @(posedge _26) begin
        if (_24)
            _52 <= _51;
        else
            _52 <= _2;
    end
    assign _78 = _74 ? _70 : _77;
    assign _3 = _78;
    always @(posedge _26) begin
        if (_24)
            _77 <= _51;
        else
            _77 <= _3;
    end
    assign _56 = _55[16:0];
    assign _69 = { _56,
                   _68 };
    assign _98 = _37 ? _69 : _55;
    assign _100 = _97 ? _51 : _98;
    assign _4 = _100;
    always @(posedge _26) begin
        if (_24)
            _55 <= _51;
        else
            _55 <= _4;
    end
    assign _70 = _37 ? _69 : _55;
    assign _104 = _96 ? _70 : _103;
    assign _5 = _104;
    always @(posedge _26) begin
        if (_24)
            _103 <= _51;
        else
            _103 <= _5;
    end
    assign _111 = _103 - _77;
    assign _112 = _90 ? _52 : _111;
    assign _110 = 14'b00000000000000;
    assign _113 = { _110,
                    _112 };
    assign _114 = _109 + _113;
    assign _115 = _106 ? _114 : _109;
    assign _6 = _115;
    always @(posedge _26) begin
        if (_24)
            _109 <= _108;
        else
            _109 <= _6;
    end
    assign _176 = 32'b00000000000000000000000000000001;
    assign _172 = 10'b0000000000;
    assign _125 = _65 - _66;
    assign _66 = 18'b000000000001100100;
    assign _160 = 2'b00;
    assign _161 = { _160,
                    _9 };
    assign _9 = instruction_mag;
    assign _120 = { _160,
                    _9 };
    assign _121 = _83 ? _120 : _118;
    assign _10 = _121;
    always @(posedge _26) begin
        if (_24)
            _118 <= _51;
        else
            _118 <= _10;
    end
    assign _155 = 8'b00000000;
    assign _156 = { _155,
                    _34 };
    assign _157 = _156 + _118;
    assign _151 = { _155,
                    _34 };
    assign _153 = _151 + _66;
    assign _154 = _153 - _127;
    assign _158 = _90 ? _157 : _154;
    assign _147 = 18'b000000000001100011;
    assign _146 = { _155,
                    _34 };
    assign _148 = _146 + _147;
    assign _123 = 7'b0000000;
    assign _128 = _127[6:0];
    assign _129 = _86 ? _128 : _124;
    assign _11 = _129;
    always @(posedge _26) begin
        if (_24)
            _124 <= _123;
        else
            _124 <= _11;
    end
    assign _142 = 11'b00000000000;
    assign _143 = { _142,
                    _124 };
    assign _32 = 10'b0000110010;
    assign _133 = _106 ? _132 : _34;
    assign _12 = _133;
    always @(posedge _26) begin
        if (_24)
            _34 <= _32;
        else
            _34 <= _12;
    end
    assign _139 = { _155,
                    _34 };
    assign _141 = _139 + _66;
    assign _144 = _141 - _143;
    assign _149 = _92 ? _148 : _144;
    assign _159 = _86 ? _158 : _149;
    assign _162 = _83 ? _161 : _159;
    assign _134 = _63[16:0];
    assign _136 = { _134,
                    gnd };
    assign _137 = _37 ? _136 : _63;
    assign _163 = _97 ? _162 : _137;
    assign _13 = _163;
    always @(posedge _26) begin
        if (_24)
            _63 <= _51;
        else
            _63 <= _13;
    end
    assign _64 = _63[17:17];
    assign _60 = _59[16:0];
    assign _65 = { _60,
                   _64 };
    assign _67 = _65 < _66;
    assign _68 = ~ _67;
    assign _126 = _68 ? _125 : _65;
    assign _164 = _37 ? _126 : _59;
    assign _166 = _97 ? _51 : _164;
    assign _14 = _166;
    always @(posedge _26) begin
        if (_24)
            _59 <= _51;
        else
            _59 <= _14;
    end
    assign _127 = _37 ? _126 : _59;
    assign _167 = _127[9:0];
    assign _168 = _49 ? _167 : _132;
    assign _15 = _168;
    always @(posedge _26) begin
        if (_24)
            _132 <= _172;
        else
            _132 <= _15;
    end
    assign _173 = _132 == _172;
    assign _174 = _90 & _173;
    assign _177 = _174 ? _176 : _108;
    assign _178 = _171 + _177;
    assign _179 = _106 ? _178 : _171;
    assign _16 = _179;
    always @(posedge _26) begin
        if (_24)
            _171 <= _108;
        else
            _171 <= _16;
    end
    assign _79 = 3'b000;
    assign _201 = 3'b001;
    assign _199 = 3'b010;
    assign _197 = 3'b101;
    assign _195 = 3'b011;
    assign _193 = 3'b100;
    assign _106 = _46 == _197;
    assign _190 = _106 ? _79 : _46;
    assign _73 = _46 == _193;
    assign _74 = _43 & _73;
    assign _192 = _74 ? _197 : _190;
    assign _194 = _96 ? _193 : _192;
    assign _196 = _92 ? _195 : _194;
    assign _188 = _49 & _90;
    assign _198 = _188 ? _197 : _196;
    assign _200 = _86 ? _199 : _198;
    assign _19 = instruction_valid;
    assign _36 = 1'b0;
    assign gnd = 1'b0;
    assign _186 = _43 ? gnd : _37;
    assign _95 = _46 == _195;
    assign _96 = _43 & _95;
    assign _21 = instruction_dir;
    assign _180 = _83 ? _21 : _90;
    assign _22 = _180;
    always @(posedge _26) begin
        if (_24)
            _90 <= _36;
        else
            _90 <= _22;
    end
    assign _91 = ~ _90;
    assign _48 = _46 == _199;
    assign _49 = _43 & _48;
    assign _92 = _49 & _91;
    assign _85 = _46 == _201;
    assign _41 = 5'b00001;
    assign vdd = 1'b1;
    assign _39 = 5'b00000;
    assign _24 = clear;
    assign _26 = clock;
    assign _184 = 5'b10010;
    assign _182 = _40 - _41;
    assign _183 = _37 ? _182 : _40;
    assign _185 = _97 ? _184 : _183;
    assign _27 = _185;
    always @(posedge _26) begin
        if (_24)
            _40 <= _39;
        else
            _40 <= _27;
    end
    assign _42 = _40 == _41;
    assign _43 = _37 & _42;
    assign _86 = _43 & _85;
    assign _87 = _83 | _86;
    assign _93 = _87 | _92;
    assign _97 = _93 | _96;
    assign _187 = _97 ? vdd : _186;
    assign _28 = _187;
    always @(posedge _26) begin
        if (_24)
            _37 <= _36;
        else
            _37 <= _28;
    end
    assign _81 = ~ _37;
    assign _82 = _80 & _81;
    assign _83 = _82 & _19;
    assign _202 = _83 ? _201 : _200;
    assign _29 = _202;
    always @(posedge _26) begin
        if (_24)
            _46 <= _79;
        else
            _46 <= _29;
    end
    assign _80 = _46 == _79;
    assign ready = _80;
    assign part1_result = _171;
    assign part2_result = _109;
    assign position = _34;

endmodule
