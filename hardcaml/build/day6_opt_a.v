module day6_opt_a (
    r3_digit,
    r3_space,
    r2_digit,
    r2_space,
    r1_digit,
    r1_space,
    r0_digit,
    r0_space,
    block_plus,
    block_start,
    clear,
    clock,
    frame_last,
    col_last,
    col_valid,
    load,
    ready,
    done_,
    part1_result,
    part2_result,
    in_block
);

    input [3:0] r3_digit;
    input r3_space;
    input [3:0] r2_digit;
    input r2_space;
    input [3:0] r1_digit;
    input r1_space;
    input [3:0] r0_digit;
    input r0_space;
    input block_plus;
    input block_start;
    input clear;
    input clock;
    input frame_last;
    input col_last;
    input col_valid;
    input load;
    output ready;
    output done_;
    output [63:0] part1_result;
    output [63:0] part2_result;
    output in_block;

    wire _57;
    wire _60;
    wire _61;
    wire _63;
    wire _1;
    reg _58;
    wire [63:0] _120;
    wire [63:0] _114;
    wire [59:0] _108;
    wire [63:0] _109;
    wire [62:0] _104;
    wire [63:0] _106;
    wire [2:0] _102;
    wire [63:0] _98;
    wire [62:0] _93;
    wire [63:0] _95;
    wire [63:0] _87;
    wire [62:0] _82;
    wire [63:0] _84;
    wire [63:0] _76;
    wire [63:0] _78;
    wire [60:0] _79;
    wire [63:0] _81;
    wire [63:0] _85;
    wire [63:0] _88;
    wire [63:0] _89;
    wire [60:0] _90;
    wire [63:0] _92;
    wire [63:0] _96;
    wire [63:0] _99;
    wire [63:0] _100;
    wire [60:0] _101;
    wire [63:0] _103;
    wire [63:0] _107;
    wire [63:0] _110;
    wire [63:0] _111;
    wire [63:0] _71;
    wire [63:0] _73;
    wire [63:0] _116;
    wire [63:0] _118;
    wire [63:0] _3;
    reg [63:0] _66;
    wire [63:0] _74;
    wire [127:0] _112;
    wire [63:0] _113;
    wire [63:0] _115;
    wire [63:0] _122;
    wire [63:0] _123;
    wire [63:0] _125;
    wire [63:0] _4;
    reg [63:0] _121;
    wire [63:0] _215;
    wire [63:0] _214;
    wire [63:0] _216;
    wire [3:0] _7;
    wire [63:0] _139;
    wire [62:0] _134;
    wire [63:0] _136;
    wire [63:0] _142;
    wire [63:0] _144;
    wire [63:0] _8;
    reg [63:0] _128;
    wire [63:0] _130;
    wire [60:0] _131;
    wire [63:0] _133;
    wire [63:0] _137;
    wire [63:0] _140;
    wire _10;
    wire [63:0] _141;
    wire [3:0] _12;
    wire [63:0] _158;
    wire [62:0] _153;
    wire [63:0] _155;
    wire [63:0] _161;
    wire [63:0] _163;
    wire [63:0] _13;
    reg [63:0] _147;
    wire [63:0] _149;
    wire [60:0] _150;
    wire [63:0] _152;
    wire [63:0] _156;
    wire [63:0] _159;
    wire _15;
    wire [63:0] _160;
    wire [127:0] _210;
    wire [63:0] _211;
    wire [3:0] _17;
    wire [63:0] _177;
    wire [62:0] _172;
    wire [63:0] _174;
    wire [63:0] _180;
    wire [63:0] _182;
    wire [63:0] _18;
    reg [63:0] _166;
    wire [63:0] _168;
    wire [60:0] _169;
    wire [63:0] _171;
    wire [63:0] _175;
    wire [63:0] _178;
    wire _20;
    wire [63:0] _179;
    wire [3:0] _22;
    wire [63:0] _196;
    wire [62:0] _191;
    wire [63:0] _193;
    wire [63:0] _199;
    wire [63:0] _201;
    wire [63:0] _23;
    reg [63:0] _185;
    wire [63:0] _187;
    wire [60:0] _188;
    wire [63:0] _190;
    wire [63:0] _194;
    wire [63:0] _197;
    wire _25;
    wire [63:0] _198;
    wire [127:0] _208;
    wire [63:0] _209;
    wire [127:0] _212;
    wire [63:0] _213;
    wire _27;
    wire _202;
    wire _204;
    wire _28;
    reg _69;
    wire _30;
    wire _54;
    wire _70;
    wire [63:0] _217;
    wire [63:0] _218;
    wire [63:0] _219;
    wire [63:0] _221;
    wire [63:0] _31;
    reg [63:0] _207;
    wire _35;
    wire _37;
    wire vdd;
    wire _39;
    wire _41;
    wire _43;
    wire _53;
    wire _55;
    wire _222;
    wire _223;
    wire _45;
    wire _225;
    wire _46;
    reg _51;
    wire _52;
    assign _57 = 1'b0;
    assign _60 = _55 ? _57 : _58;
    assign _61 = _54 ? vdd : _60;
    assign _63 = _45 ? _57 : _61;
    assign _1 = _63;
    always @(posedge _37) begin
        if (_35)
            _58 <= _57;
        else
            _58 <= _1;
    end
    assign _120 = 64'b0000000000000000000000000000000000000000000000000000000000000000;
    assign _114 = _74 + _111;
    assign _108 = 60'b000000000000000000000000000000000000000000000000000000000000;
    assign _109 = { _108,
                    _7 };
    assign _104 = _100[62:0];
    assign _106 = { _104,
                    _57 };
    assign _102 = 3'b000;
    assign _98 = { _108,
                   _12 };
    assign _93 = _89[62:0];
    assign _95 = { _93,
                   _57 };
    assign _87 = { _108,
                   _17 };
    assign _82 = _78[62:0];
    assign _84 = { _82,
                   _57 };
    assign _76 = { _108,
                   _22 };
    assign _78 = _25 ? _120 : _76;
    assign _79 = _78[60:0];
    assign _81 = { _79,
                   _102 };
    assign _85 = _81 + _84;
    assign _88 = _85 + _87;
    assign _89 = _20 ? _78 : _88;
    assign _90 = _89[60:0];
    assign _92 = { _90,
                   _102 };
    assign _96 = _92 + _95;
    assign _99 = _96 + _98;
    assign _100 = _15 ? _89 : _99;
    assign _101 = _100[60:0];
    assign _103 = { _101,
                    _102 };
    assign _107 = _103 + _106;
    assign _110 = _107 + _109;
    assign _111 = _10 ? _100 : _110;
    assign _71 = 64'b0000000000000000000000000000000000000000000000000000000000000001;
    assign _73 = _27 ? _120 : _71;
    assign _116 = _53 ? _115 : _66;
    assign _118 = _45 ? _120 : _116;
    assign _3 = _118;
    always @(posedge _37) begin
        if (_35)
            _66 <= _120;
        else
            _66 <= _3;
    end
    assign _74 = _54 ? _73 : _66;
    assign _112 = _74 * _111;
    assign _113 = _112[63:0];
    assign _115 = _70 ? _114 : _113;
    assign _122 = _121 + _115;
    assign _123 = _55 ? _122 : _121;
    assign _125 = _45 ? _120 : _123;
    assign _4 = _125;
    always @(posedge _37) begin
        if (_35)
            _121 <= _120;
        else
            _121 <= _4;
    end
    assign _215 = _160 + _141;
    assign _214 = _198 + _179;
    assign _216 = _214 + _215;
    assign _7 = r3_digit;
    assign _139 = { _108,
                    _7 };
    assign _134 = _130[62:0];
    assign _136 = { _134,
                    _57 };
    assign _142 = _53 ? _141 : _128;
    assign _144 = _45 ? _120 : _142;
    assign _8 = _144;
    always @(posedge _37) begin
        if (_35)
            _128 <= _120;
        else
            _128 <= _8;
    end
    assign _130 = _54 ? _120 : _128;
    assign _131 = _130[60:0];
    assign _133 = { _131,
                    _102 };
    assign _137 = _133 + _136;
    assign _140 = _137 + _139;
    assign _10 = r3_space;
    assign _141 = _10 ? _130 : _140;
    assign _12 = r2_digit;
    assign _158 = { _108,
                    _12 };
    assign _153 = _149[62:0];
    assign _155 = { _153,
                    _57 };
    assign _161 = _53 ? _160 : _147;
    assign _163 = _45 ? _120 : _161;
    assign _13 = _163;
    always @(posedge _37) begin
        if (_35)
            _147 <= _120;
        else
            _147 <= _13;
    end
    assign _149 = _54 ? _120 : _147;
    assign _150 = _149[60:0];
    assign _152 = { _150,
                    _102 };
    assign _156 = _152 + _155;
    assign _159 = _156 + _158;
    assign _15 = r2_space;
    assign _160 = _15 ? _149 : _159;
    assign _210 = _160 * _141;
    assign _211 = _210[63:0];
    assign _17 = r1_digit;
    assign _177 = { _108,
                    _17 };
    assign _172 = _168[62:0];
    assign _174 = { _172,
                    _57 };
    assign _180 = _53 ? _179 : _166;
    assign _182 = _45 ? _120 : _180;
    assign _18 = _182;
    always @(posedge _37) begin
        if (_35)
            _166 <= _120;
        else
            _166 <= _18;
    end
    assign _168 = _54 ? _120 : _166;
    assign _169 = _168[60:0];
    assign _171 = { _169,
                    _102 };
    assign _175 = _171 + _174;
    assign _178 = _175 + _177;
    assign _20 = r1_space;
    assign _179 = _20 ? _168 : _178;
    assign _22 = r0_digit;
    assign _196 = { _108,
                    _22 };
    assign _191 = _187[62:0];
    assign _193 = { _191,
                    _57 };
    assign _199 = _53 ? _198 : _185;
    assign _201 = _45 ? _120 : _199;
    assign _23 = _201;
    always @(posedge _37) begin
        if (_35)
            _185 <= _120;
        else
            _185 <= _23;
    end
    assign _187 = _54 ? _120 : _185;
    assign _188 = _187[60:0];
    assign _190 = { _188,
                    _102 };
    assign _194 = _190 + _193;
    assign _197 = _194 + _196;
    assign _25 = r0_space;
    assign _198 = _25 ? _187 : _197;
    assign _208 = _198 * _179;
    assign _209 = _208[63:0];
    assign _212 = _209 * _211;
    assign _213 = _212[63:0];
    assign _27 = block_plus;
    assign _202 = _54 ? _27 : _69;
    assign _204 = _45 ? _57 : _202;
    assign _28 = _204;
    always @(posedge _37) begin
        if (_35)
            _69 <= _57;
        else
            _69 <= _28;
    end
    assign _30 = block_start;
    assign _54 = _53 & _30;
    assign _70 = _54 ? _27 : _69;
    assign _217 = _70 ? _216 : _213;
    assign _218 = _207 + _217;
    assign _219 = _55 ? _218 : _207;
    assign _221 = _45 ? _120 : _219;
    assign _31 = _221;
    always @(posedge _37) begin
        if (_35)
            _207 <= _120;
        else
            _207 <= _31;
    end
    assign _35 = clear;
    assign _37 = clock;
    assign vdd = 1'b1;
    assign _39 = frame_last;
    assign _41 = col_last;
    assign _43 = col_valid;
    assign _53 = _52 & _43;
    assign _55 = _53 & _41;
    assign _222 = _55 & _39;
    assign _223 = _222 ? vdd : _51;
    assign _45 = load;
    assign _225 = _45 ? _57 : _223;
    assign _46 = _225;
    always @(posedge _37) begin
        if (_35)
            _51 <= _57;
        else
            _51 <= _46;
    end
    assign _52 = ~ _51;
    assign ready = _52;
    assign done_ = _51;
    assign part1_result = _207;
    assign part2_result = _121;
    assign in_block = _58;

endmodule
