module day11 (
    count,
    clear,
    clock,
    count_last,
    count_valid,
    load,
    ready,
    done_,
    part1_result,
    part2_result,
    idx
);

    input [63:0] count;
    input clear;
    input clock;
    input count_last;
    input count_valid;
    input load;
    output ready;
    output done_;
    output [63:0] part1_result;
    output [63:0] part2_result;
    output [2:0] idx;

    wire [63:0] _40;
    wire [2:0] _36;
    wire _37;
    wire _38;
    wire [63:0] _42;
    wire [63:0] _44;
    wire [63:0] _2;
    reg [63:0] _41;
    wire [2:0] _45;
    wire _46;
    wire _47;
    wire [63:0] _51;
    wire [63:0] _53;
    wire [63:0] _3;
    reg [63:0] _50;
    wire [2:0] _54;
    wire _55;
    wire _56;
    wire [63:0] _60;
    wire [63:0] _62;
    wire [63:0] _4;
    reg [63:0] _59;
    wire [127:0] _94;
    wire [63:0] _95;
    wire [127:0] _96;
    wire [63:0] _97;
    wire [2:0] _63;
    wire _64;
    wire _65;
    wire [63:0] _69;
    wire [63:0] _71;
    wire [63:0] _5;
    reg [63:0] _68;
    wire [2:0] _72;
    wire _73;
    wire _74;
    wire [63:0] _78;
    wire [63:0] _80;
    wire [63:0] _6;
    reg [63:0] _77;
    wire [2:0] _81;
    wire _82;
    wire _83;
    wire [63:0] _87;
    wire [63:0] _89;
    wire [63:0] _7;
    reg [63:0] _86;
    wire [127:0] _90;
    wire [63:0] _91;
    wire [127:0] _92;
    wire [63:0] _93;
    wire [63:0] _98;
    wire [63:0] _10;
    wire [2:0] _104;
    wire [2:0] _100;
    wire [2:0] _101;
    wire [2:0] _103;
    wire [2:0] _11;
    reg [2:0] _30;
    wire _105;
    wire _106;
    wire [63:0] _110;
    wire [63:0] _112;
    wire [63:0] _12;
    reg [63:0] _109;
    wire _32;
    wire _16;
    wire _18;
    wire vdd;
    wire _20;
    wire _22;
    wire _35;
    wire _113;
    wire _114;
    wire _24;
    wire _116;
    wire _25;
    reg _33;
    wire _34;
    assign _40 = 64'b0000000000000000000000000000000000000000000000000000000000000000;
    assign _36 = 3'b110;
    assign _37 = _30 == _36;
    assign _38 = _35 & _37;
    assign _42 = _38 ? _10 : _41;
    assign _44 = _24 ? _40 : _42;
    assign _2 = _44;
    always @(posedge _18) begin
        if (_16)
            _41 <= _40;
        else
            _41 <= _2;
    end
    assign _45 = 3'b101;
    assign _46 = _30 == _45;
    assign _47 = _35 & _46;
    assign _51 = _47 ? _10 : _50;
    assign _53 = _24 ? _40 : _51;
    assign _3 = _53;
    always @(posedge _18) begin
        if (_16)
            _50 <= _40;
        else
            _50 <= _3;
    end
    assign _54 = 3'b100;
    assign _55 = _30 == _54;
    assign _56 = _35 & _55;
    assign _60 = _56 ? _10 : _59;
    assign _62 = _24 ? _40 : _60;
    assign _4 = _62;
    always @(posedge _18) begin
        if (_16)
            _59 <= _40;
        else
            _59 <= _4;
    end
    assign _94 = _59 * _50;
    assign _95 = _94[63:0];
    assign _96 = _95 * _41;
    assign _97 = _96[63:0];
    assign _63 = 3'b011;
    assign _64 = _30 == _63;
    assign _65 = _35 & _64;
    assign _69 = _65 ? _10 : _68;
    assign _71 = _24 ? _40 : _69;
    assign _5 = _71;
    always @(posedge _18) begin
        if (_16)
            _68 <= _40;
        else
            _68 <= _5;
    end
    assign _72 = 3'b010;
    assign _73 = _30 == _72;
    assign _74 = _35 & _73;
    assign _78 = _74 ? _10 : _77;
    assign _80 = _24 ? _40 : _78;
    assign _6 = _80;
    always @(posedge _18) begin
        if (_16)
            _77 <= _40;
        else
            _77 <= _6;
    end
    assign _81 = 3'b001;
    assign _82 = _30 == _81;
    assign _83 = _35 & _82;
    assign _87 = _83 ? _10 : _86;
    assign _89 = _24 ? _40 : _87;
    assign _7 = _89;
    always @(posedge _18) begin
        if (_16)
            _86 <= _40;
        else
            _86 <= _7;
    end
    assign _90 = _86 * _77;
    assign _91 = _90[63:0];
    assign _92 = _91 * _68;
    assign _93 = _92[63:0];
    assign _98 = _93 + _97;
    assign _10 = count;
    assign _104 = 3'b000;
    assign _100 = _30 + _81;
    assign _101 = _35 ? _100 : _30;
    assign _103 = _24 ? _104 : _101;
    assign _11 = _103;
    always @(posedge _18) begin
        if (_16)
            _30 <= _104;
        else
            _30 <= _11;
    end
    assign _105 = _30 == _104;
    assign _106 = _35 & _105;
    assign _110 = _106 ? _10 : _109;
    assign _112 = _24 ? _40 : _110;
    assign _12 = _112;
    always @(posedge _18) begin
        if (_16)
            _109 <= _40;
        else
            _109 <= _12;
    end
    assign _32 = 1'b0;
    assign _16 = clear;
    assign _18 = clock;
    assign vdd = 1'b1;
    assign _20 = count_last;
    assign _22 = count_valid;
    assign _35 = _34 & _22;
    assign _113 = _35 & _20;
    assign _114 = _113 ? vdd : _33;
    assign _24 = load;
    assign _116 = _24 ? _32 : _114;
    assign _25 = _116;
    always @(posedge _18) begin
        if (_16)
            _33 <= _32;
        else
            _33 <= _25;
    end
    assign _34 = ~ _33;
    assign ready = _34;
    assign done_ = _33;
    assign part1_result = _109;
    assign part2_result = _98;
    assign idx = _30;

endmodule
