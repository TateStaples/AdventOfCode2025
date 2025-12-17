module day12_opt_b (
    num,
    clear,
    clock,
    num_last,
    num_valid,
    load,
    ready,
    done_,
    part1_result,
    part2_result,
    idx_mod8
);

    input [31:0] num;
    input clear;
    input clock;
    input num_last;
    input num_valid;
    input load;
    output ready;
    output done_;
    output [63:0] part1_result;
    output [63:0] part2_result;
    output [2:0] idx_mod8;

    wire [63:0] _29;
    wire [63:0] _694;
    wire [31:0] _58;
    wire [2:0] _53;
    wire _54;
    wire _55;
    wire _51;
    wire _52;
    wire _56;
    wire [31:0] _61;
    wire _46;
    wire _47;
    wire _50;
    wire [31:0] _63;
    wire _41;
    wire _42;
    wire _45;
    wire [31:0] _65;
    wire _40;
    wire [31:0] _66;
    wire [31:0] _68;
    wire [31:0] _3;
    reg [31:0] _59;
    wire [31:0] _60;
    wire [63:0] _690;
    wire _681;
    wire [31:0] _678;
    wire [31:0] _679;
    wire [30:0] _680;
    wire [31:0] _682;
    wire _683;
    wire _684;
    wire _672;
    wire [31:0] _669;
    wire [31:0] _670;
    wire [30:0] _671;
    wire [31:0] _673;
    wire _674;
    wire _675;
    wire _663;
    wire [31:0] _660;
    wire [31:0] _661;
    wire [30:0] _662;
    wire [31:0] _664;
    wire _665;
    wire _666;
    wire _654;
    wire [31:0] _651;
    wire [31:0] _652;
    wire [30:0] _653;
    wire [31:0] _655;
    wire _656;
    wire _657;
    wire _645;
    wire [31:0] _642;
    wire [31:0] _643;
    wire [30:0] _644;
    wire [31:0] _646;
    wire _647;
    wire _648;
    wire _636;
    wire [31:0] _633;
    wire [31:0] _634;
    wire [30:0] _635;
    wire [31:0] _637;
    wire _638;
    wire _639;
    wire _627;
    wire [31:0] _624;
    wire [31:0] _625;
    wire [30:0] _626;
    wire [31:0] _628;
    wire _629;
    wire _630;
    wire _618;
    wire [31:0] _615;
    wire [31:0] _616;
    wire [30:0] _617;
    wire [31:0] _619;
    wire _620;
    wire _621;
    wire _609;
    wire [31:0] _606;
    wire [31:0] _607;
    wire [30:0] _608;
    wire [31:0] _610;
    wire _611;
    wire _612;
    wire _600;
    wire [31:0] _597;
    wire [31:0] _598;
    wire [30:0] _599;
    wire [31:0] _601;
    wire _602;
    wire _603;
    wire _591;
    wire [31:0] _588;
    wire [31:0] _589;
    wire [30:0] _590;
    wire [31:0] _592;
    wire _593;
    wire _594;
    wire _582;
    wire [31:0] _579;
    wire [31:0] _580;
    wire [30:0] _581;
    wire [31:0] _583;
    wire _584;
    wire _585;
    wire _573;
    wire [31:0] _570;
    wire [31:0] _571;
    wire [30:0] _572;
    wire [31:0] _574;
    wire _575;
    wire _576;
    wire _564;
    wire [31:0] _561;
    wire [31:0] _562;
    wire [30:0] _563;
    wire [31:0] _565;
    wire _566;
    wire _567;
    wire _555;
    wire [31:0] _552;
    wire [31:0] _553;
    wire [30:0] _554;
    wire [31:0] _556;
    wire _557;
    wire _558;
    wire _546;
    wire [31:0] _543;
    wire [31:0] _544;
    wire [30:0] _545;
    wire [31:0] _547;
    wire _548;
    wire _549;
    wire _537;
    wire [31:0] _534;
    wire [31:0] _535;
    wire [30:0] _536;
    wire [31:0] _538;
    wire _539;
    wire _540;
    wire _528;
    wire [31:0] _525;
    wire [31:0] _526;
    wire [30:0] _527;
    wire [31:0] _529;
    wire _530;
    wire _531;
    wire _519;
    wire [31:0] _516;
    wire [31:0] _517;
    wire [30:0] _518;
    wire [31:0] _520;
    wire _521;
    wire _522;
    wire _510;
    wire [31:0] _507;
    wire [31:0] _508;
    wire [30:0] _509;
    wire [31:0] _511;
    wire _512;
    wire _513;
    wire _501;
    wire [31:0] _498;
    wire [31:0] _499;
    wire [30:0] _500;
    wire [31:0] _502;
    wire _503;
    wire _504;
    wire _492;
    wire [31:0] _489;
    wire [31:0] _490;
    wire [30:0] _491;
    wire [31:0] _493;
    wire _494;
    wire _495;
    wire _483;
    wire [31:0] _480;
    wire [31:0] _481;
    wire [30:0] _482;
    wire [31:0] _484;
    wire _485;
    wire _486;
    wire _474;
    wire [31:0] _471;
    wire [31:0] _472;
    wire [30:0] _473;
    wire [31:0] _475;
    wire _476;
    wire _477;
    wire _465;
    wire [31:0] _462;
    wire [31:0] _463;
    wire [30:0] _464;
    wire [31:0] _466;
    wire _467;
    wire _468;
    wire _456;
    wire [31:0] _453;
    wire [31:0] _454;
    wire [30:0] _455;
    wire [31:0] _457;
    wire _458;
    wire _459;
    wire _447;
    wire [31:0] _444;
    wire [31:0] _445;
    wire [30:0] _446;
    wire [31:0] _448;
    wire _449;
    wire _450;
    wire _438;
    wire [31:0] _435;
    wire [31:0] _436;
    wire [30:0] _437;
    wire [31:0] _439;
    wire _440;
    wire _441;
    wire _429;
    wire [31:0] _426;
    wire [31:0] _427;
    wire [30:0] _428;
    wire [31:0] _430;
    wire _431;
    wire _432;
    wire _420;
    wire [31:0] _417;
    wire [31:0] _418;
    wire [30:0] _419;
    wire [31:0] _421;
    wire _422;
    wire _423;
    wire _411;
    wire [31:0] _408;
    wire [31:0] _409;
    wire [30:0] _410;
    wire [31:0] _412;
    wire _413;
    wire _414;
    wire [31:0] _403;
    wire [2:0] _48;
    wire _49;
    wire _69;
    wire _70;
    wire _71;
    wire [31:0] _75;
    wire [31:0] _77;
    wire [31:0] _4;
    reg [31:0] _74;
    wire _401;
    wire [30:0] _400;
    wire [31:0] _402;
    wire _404;
    wire _405;
    wire [31:0] _406;
    wire [30:0] _407;
    wire [31:0] _415;
    wire [30:0] _416;
    wire [31:0] _424;
    wire [30:0] _425;
    wire [31:0] _433;
    wire [30:0] _434;
    wire [31:0] _442;
    wire [30:0] _443;
    wire [31:0] _451;
    wire [30:0] _452;
    wire [31:0] _460;
    wire [30:0] _461;
    wire [31:0] _469;
    wire [30:0] _470;
    wire [31:0] _478;
    wire [30:0] _479;
    wire [31:0] _487;
    wire [30:0] _488;
    wire [31:0] _496;
    wire [30:0] _497;
    wire [31:0] _505;
    wire [30:0] _506;
    wire [31:0] _514;
    wire [30:0] _515;
    wire [31:0] _523;
    wire [30:0] _524;
    wire [31:0] _532;
    wire [30:0] _533;
    wire [31:0] _541;
    wire [30:0] _542;
    wire [31:0] _550;
    wire [30:0] _551;
    wire [31:0] _559;
    wire [30:0] _560;
    wire [31:0] _568;
    wire [30:0] _569;
    wire [31:0] _577;
    wire [30:0] _578;
    wire [31:0] _586;
    wire [30:0] _587;
    wire [31:0] _595;
    wire [30:0] _596;
    wire [31:0] _604;
    wire [30:0] _605;
    wire [31:0] _613;
    wire [30:0] _614;
    wire [31:0] _622;
    wire [30:0] _623;
    wire [31:0] _631;
    wire [30:0] _632;
    wire [31:0] _640;
    wire [30:0] _641;
    wire [31:0] _649;
    wire [30:0] _650;
    wire [31:0] _658;
    wire [30:0] _659;
    wire [31:0] _667;
    wire [30:0] _668;
    wire [31:0] _676;
    wire [30:0] _677;
    wire [31:0] _685;
    wire [63:0] _686;
    wire _392;
    wire [31:0] _389;
    wire [31:0] _390;
    wire [30:0] _391;
    wire [31:0] _393;
    wire _394;
    wire _395;
    wire _383;
    wire [31:0] _380;
    wire [31:0] _381;
    wire [30:0] _382;
    wire [31:0] _384;
    wire _385;
    wire _386;
    wire _374;
    wire [31:0] _371;
    wire [31:0] _372;
    wire [30:0] _373;
    wire [31:0] _375;
    wire _376;
    wire _377;
    wire _365;
    wire [31:0] _362;
    wire [31:0] _363;
    wire [30:0] _364;
    wire [31:0] _366;
    wire _367;
    wire _368;
    wire _356;
    wire [31:0] _353;
    wire [31:0] _354;
    wire [30:0] _355;
    wire [31:0] _357;
    wire _358;
    wire _359;
    wire _347;
    wire [31:0] _344;
    wire [31:0] _345;
    wire [30:0] _346;
    wire [31:0] _348;
    wire _349;
    wire _350;
    wire _338;
    wire [31:0] _335;
    wire [31:0] _336;
    wire [30:0] _337;
    wire [31:0] _339;
    wire _340;
    wire _341;
    wire _329;
    wire [31:0] _326;
    wire [31:0] _327;
    wire [30:0] _328;
    wire [31:0] _330;
    wire _331;
    wire _332;
    wire _320;
    wire [31:0] _317;
    wire [31:0] _318;
    wire [30:0] _319;
    wire [31:0] _321;
    wire _322;
    wire _323;
    wire _311;
    wire [31:0] _308;
    wire [31:0] _309;
    wire [30:0] _310;
    wire [31:0] _312;
    wire _313;
    wire _314;
    wire _302;
    wire [31:0] _299;
    wire [31:0] _300;
    wire [30:0] _301;
    wire [31:0] _303;
    wire _304;
    wire _305;
    wire _293;
    wire [31:0] _290;
    wire [31:0] _291;
    wire [30:0] _292;
    wire [31:0] _294;
    wire _295;
    wire _296;
    wire _284;
    wire [31:0] _281;
    wire [31:0] _282;
    wire [30:0] _283;
    wire [31:0] _285;
    wire _286;
    wire _287;
    wire _275;
    wire [31:0] _272;
    wire [31:0] _273;
    wire [30:0] _274;
    wire [31:0] _276;
    wire _277;
    wire _278;
    wire _266;
    wire [31:0] _263;
    wire [31:0] _264;
    wire [30:0] _265;
    wire [31:0] _267;
    wire _268;
    wire _269;
    wire _257;
    wire [31:0] _254;
    wire [31:0] _255;
    wire [30:0] _256;
    wire [31:0] _258;
    wire _259;
    wire _260;
    wire _248;
    wire [31:0] _245;
    wire [31:0] _246;
    wire [30:0] _247;
    wire [31:0] _249;
    wire _250;
    wire _251;
    wire _239;
    wire [31:0] _236;
    wire [31:0] _237;
    wire [30:0] _238;
    wire [31:0] _240;
    wire _241;
    wire _242;
    wire _230;
    wire [31:0] _227;
    wire [31:0] _228;
    wire [30:0] _229;
    wire [31:0] _231;
    wire _232;
    wire _233;
    wire _221;
    wire [31:0] _218;
    wire [31:0] _219;
    wire [30:0] _220;
    wire [31:0] _222;
    wire _223;
    wire _224;
    wire _212;
    wire [31:0] _209;
    wire [31:0] _210;
    wire [30:0] _211;
    wire [31:0] _213;
    wire _214;
    wire _215;
    wire _203;
    wire [31:0] _200;
    wire [31:0] _201;
    wire [30:0] _202;
    wire [31:0] _204;
    wire _205;
    wire _206;
    wire _194;
    wire [31:0] _191;
    wire [31:0] _192;
    wire [30:0] _193;
    wire [31:0] _195;
    wire _196;
    wire _197;
    wire _185;
    wire [31:0] _182;
    wire [31:0] _183;
    wire [30:0] _184;
    wire [31:0] _186;
    wire _187;
    wire _188;
    wire _176;
    wire [31:0] _173;
    wire [31:0] _174;
    wire [30:0] _175;
    wire [31:0] _177;
    wire _178;
    wire _179;
    wire _167;
    wire [31:0] _164;
    wire [31:0] _165;
    wire [30:0] _166;
    wire [31:0] _168;
    wire _169;
    wire _170;
    wire _158;
    wire [31:0] _155;
    wire [31:0] _156;
    wire [30:0] _157;
    wire [31:0] _159;
    wire _160;
    wire _161;
    wire _149;
    wire [31:0] _146;
    wire [31:0] _147;
    wire [30:0] _148;
    wire [31:0] _150;
    wire _151;
    wire _152;
    wire _140;
    wire [31:0] _137;
    wire [31:0] _138;
    wire [30:0] _139;
    wire [31:0] _141;
    wire _142;
    wire _143;
    wire _131;
    wire [31:0] _128;
    wire [31:0] _129;
    wire [30:0] _130;
    wire [31:0] _132;
    wire _133;
    wire _134;
    wire _122;
    wire [31:0] _119;
    wire [31:0] _120;
    wire [30:0] _121;
    wire [31:0] _123;
    wire _124;
    wire _125;
    wire [31:0] _6;
    wire [2:0] _43;
    wire _44;
    wire _78;
    wire _79;
    wire _80;
    wire [31:0] _84;
    wire [31:0] _86;
    wire [31:0] _7;
    reg [31:0] _83;
    wire _112;
    wire [31:0] _113;
    wire _115;
    wire _116;
    wire [31:0] _117;
    wire [30:0] _118;
    wire [31:0] _126;
    wire [30:0] _127;
    wire [31:0] _135;
    wire [30:0] _136;
    wire [31:0] _144;
    wire [30:0] _145;
    wire [31:0] _153;
    wire [30:0] _154;
    wire [31:0] _162;
    wire [30:0] _163;
    wire [31:0] _171;
    wire [30:0] _172;
    wire [31:0] _180;
    wire [30:0] _181;
    wire [31:0] _189;
    wire [30:0] _190;
    wire [31:0] _198;
    wire [30:0] _199;
    wire [31:0] _207;
    wire [30:0] _208;
    wire [31:0] _216;
    wire [30:0] _217;
    wire [31:0] _225;
    wire [30:0] _226;
    wire [31:0] _234;
    wire [30:0] _235;
    wire [31:0] _243;
    wire [30:0] _244;
    wire [31:0] _252;
    wire [30:0] _253;
    wire [31:0] _261;
    wire [30:0] _262;
    wire [31:0] _270;
    wire [30:0] _271;
    wire [31:0] _279;
    wire [30:0] _280;
    wire [31:0] _288;
    wire [30:0] _289;
    wire [31:0] _297;
    wire [30:0] _298;
    wire [31:0] _306;
    wire [30:0] _307;
    wire [31:0] _315;
    wire [30:0] _316;
    wire [31:0] _324;
    wire [30:0] _325;
    wire [31:0] _333;
    wire [30:0] _334;
    wire [31:0] _342;
    wire [30:0] _343;
    wire [31:0] _351;
    wire [30:0] _352;
    wire [31:0] _360;
    wire [30:0] _361;
    wire [31:0] _369;
    wire [30:0] _370;
    wire [31:0] _378;
    wire [30:0] _379;
    wire [31:0] _387;
    wire [30:0] _388;
    wire [31:0] _396;
    wire [63:0] _397;
    wire [127:0] _687;
    wire [63:0] _688;
    wire _691;
    wire _692;
    wire [63:0] _695;
    wire [63:0] _696;
    wire [2:0] _94;
    wire [2:0] _98;
    wire [2:0] _99;
    wire [2:0] _101;
    wire [2:0] _38;
    wire [2:0] _89;
    wire _87;
    wire [2:0] _90;
    wire [2:0] _92;
    wire [2:0] _8;
    reg [2:0] _37;
    wire _39;
    wire _93;
    wire [2:0] _103;
    wire [2:0] _105;
    wire [2:0] _9;
    reg [2:0] _28;
    wire _95;
    wire _96;
    wire [63:0] _697;
    wire [63:0] _699;
    wire [63:0] _10;
    reg [63:0] _108;
    wire _31;
    wire _14;
    wire _16;
    wire vdd;
    wire _18;
    wire _20;
    wire _34;
    wire _700;
    wire _701;
    wire _22;
    wire _703;
    wire _23;
    reg _32;
    wire _33;
    assign _29 = 64'b0000000000000000000000000000000000000000000000000000000000000000;
    assign _694 = 64'b0000000000000000000000000000000000000000000000000000000000000001;
    assign _58 = 32'b00000000000000000000000000000000;
    assign _53 = 3'b010;
    assign _54 = _28 < _53;
    assign _55 = ~ _54;
    assign _51 = ~ _39;
    assign _52 = _34 & _51;
    assign _56 = _52 & _55;
    assign _61 = _56 ? _60 : _59;
    assign _46 = ~ _39;
    assign _47 = _34 & _46;
    assign _50 = _47 & _49;
    assign _63 = _50 ? _58 : _61;
    assign _41 = ~ _39;
    assign _42 = _34 & _41;
    assign _45 = _42 & _44;
    assign _65 = _45 ? _58 : _63;
    assign _40 = _34 & _39;
    assign _66 = _40 ? _59 : _65;
    assign _68 = _22 ? _58 : _66;
    assign _3 = _68;
    always @(posedge _16) begin
        if (_14)
            _59 <= _58;
        else
            _59 <= _3;
    end
    assign _60 = _59 + _6;
    assign _690 = { _58,
                    _60 };
    assign _681 = _74[0:0];
    assign _678 = _673 - _403;
    assign _679 = _675 ? _678 : _673;
    assign _680 = _679[30:0];
    assign _682 = { _680,
                    _681 };
    assign _683 = _682 < _403;
    assign _684 = ~ _683;
    assign _672 = _74[1:1];
    assign _669 = _664 - _403;
    assign _670 = _666 ? _669 : _664;
    assign _671 = _670[30:0];
    assign _673 = { _671,
                    _672 };
    assign _674 = _673 < _403;
    assign _675 = ~ _674;
    assign _663 = _74[2:2];
    assign _660 = _655 - _403;
    assign _661 = _657 ? _660 : _655;
    assign _662 = _661[30:0];
    assign _664 = { _662,
                    _663 };
    assign _665 = _664 < _403;
    assign _666 = ~ _665;
    assign _654 = _74[3:3];
    assign _651 = _646 - _403;
    assign _652 = _648 ? _651 : _646;
    assign _653 = _652[30:0];
    assign _655 = { _653,
                    _654 };
    assign _656 = _655 < _403;
    assign _657 = ~ _656;
    assign _645 = _74[4:4];
    assign _642 = _637 - _403;
    assign _643 = _639 ? _642 : _637;
    assign _644 = _643[30:0];
    assign _646 = { _644,
                    _645 };
    assign _647 = _646 < _403;
    assign _648 = ~ _647;
    assign _636 = _74[5:5];
    assign _633 = _628 - _403;
    assign _634 = _630 ? _633 : _628;
    assign _635 = _634[30:0];
    assign _637 = { _635,
                    _636 };
    assign _638 = _637 < _403;
    assign _639 = ~ _638;
    assign _627 = _74[6:6];
    assign _624 = _619 - _403;
    assign _625 = _621 ? _624 : _619;
    assign _626 = _625[30:0];
    assign _628 = { _626,
                    _627 };
    assign _629 = _628 < _403;
    assign _630 = ~ _629;
    assign _618 = _74[7:7];
    assign _615 = _610 - _403;
    assign _616 = _612 ? _615 : _610;
    assign _617 = _616[30:0];
    assign _619 = { _617,
                    _618 };
    assign _620 = _619 < _403;
    assign _621 = ~ _620;
    assign _609 = _74[8:8];
    assign _606 = _601 - _403;
    assign _607 = _603 ? _606 : _601;
    assign _608 = _607[30:0];
    assign _610 = { _608,
                    _609 };
    assign _611 = _610 < _403;
    assign _612 = ~ _611;
    assign _600 = _74[9:9];
    assign _597 = _592 - _403;
    assign _598 = _594 ? _597 : _592;
    assign _599 = _598[30:0];
    assign _601 = { _599,
                    _600 };
    assign _602 = _601 < _403;
    assign _603 = ~ _602;
    assign _591 = _74[10:10];
    assign _588 = _583 - _403;
    assign _589 = _585 ? _588 : _583;
    assign _590 = _589[30:0];
    assign _592 = { _590,
                    _591 };
    assign _593 = _592 < _403;
    assign _594 = ~ _593;
    assign _582 = _74[11:11];
    assign _579 = _574 - _403;
    assign _580 = _576 ? _579 : _574;
    assign _581 = _580[30:0];
    assign _583 = { _581,
                    _582 };
    assign _584 = _583 < _403;
    assign _585 = ~ _584;
    assign _573 = _74[12:12];
    assign _570 = _565 - _403;
    assign _571 = _567 ? _570 : _565;
    assign _572 = _571[30:0];
    assign _574 = { _572,
                    _573 };
    assign _575 = _574 < _403;
    assign _576 = ~ _575;
    assign _564 = _74[13:13];
    assign _561 = _556 - _403;
    assign _562 = _558 ? _561 : _556;
    assign _563 = _562[30:0];
    assign _565 = { _563,
                    _564 };
    assign _566 = _565 < _403;
    assign _567 = ~ _566;
    assign _555 = _74[14:14];
    assign _552 = _547 - _403;
    assign _553 = _549 ? _552 : _547;
    assign _554 = _553[30:0];
    assign _556 = { _554,
                    _555 };
    assign _557 = _556 < _403;
    assign _558 = ~ _557;
    assign _546 = _74[15:15];
    assign _543 = _538 - _403;
    assign _544 = _540 ? _543 : _538;
    assign _545 = _544[30:0];
    assign _547 = { _545,
                    _546 };
    assign _548 = _547 < _403;
    assign _549 = ~ _548;
    assign _537 = _74[16:16];
    assign _534 = _529 - _403;
    assign _535 = _531 ? _534 : _529;
    assign _536 = _535[30:0];
    assign _538 = { _536,
                    _537 };
    assign _539 = _538 < _403;
    assign _540 = ~ _539;
    assign _528 = _74[17:17];
    assign _525 = _520 - _403;
    assign _526 = _522 ? _525 : _520;
    assign _527 = _526[30:0];
    assign _529 = { _527,
                    _528 };
    assign _530 = _529 < _403;
    assign _531 = ~ _530;
    assign _519 = _74[18:18];
    assign _516 = _511 - _403;
    assign _517 = _513 ? _516 : _511;
    assign _518 = _517[30:0];
    assign _520 = { _518,
                    _519 };
    assign _521 = _520 < _403;
    assign _522 = ~ _521;
    assign _510 = _74[19:19];
    assign _507 = _502 - _403;
    assign _508 = _504 ? _507 : _502;
    assign _509 = _508[30:0];
    assign _511 = { _509,
                    _510 };
    assign _512 = _511 < _403;
    assign _513 = ~ _512;
    assign _501 = _74[20:20];
    assign _498 = _493 - _403;
    assign _499 = _495 ? _498 : _493;
    assign _500 = _499[30:0];
    assign _502 = { _500,
                    _501 };
    assign _503 = _502 < _403;
    assign _504 = ~ _503;
    assign _492 = _74[21:21];
    assign _489 = _484 - _403;
    assign _490 = _486 ? _489 : _484;
    assign _491 = _490[30:0];
    assign _493 = { _491,
                    _492 };
    assign _494 = _493 < _403;
    assign _495 = ~ _494;
    assign _483 = _74[22:22];
    assign _480 = _475 - _403;
    assign _481 = _477 ? _480 : _475;
    assign _482 = _481[30:0];
    assign _484 = { _482,
                    _483 };
    assign _485 = _484 < _403;
    assign _486 = ~ _485;
    assign _474 = _74[23:23];
    assign _471 = _466 - _403;
    assign _472 = _468 ? _471 : _466;
    assign _473 = _472[30:0];
    assign _475 = { _473,
                    _474 };
    assign _476 = _475 < _403;
    assign _477 = ~ _476;
    assign _465 = _74[24:24];
    assign _462 = _457 - _403;
    assign _463 = _459 ? _462 : _457;
    assign _464 = _463[30:0];
    assign _466 = { _464,
                    _465 };
    assign _467 = _466 < _403;
    assign _468 = ~ _467;
    assign _456 = _74[25:25];
    assign _453 = _448 - _403;
    assign _454 = _450 ? _453 : _448;
    assign _455 = _454[30:0];
    assign _457 = { _455,
                    _456 };
    assign _458 = _457 < _403;
    assign _459 = ~ _458;
    assign _447 = _74[26:26];
    assign _444 = _439 - _403;
    assign _445 = _441 ? _444 : _439;
    assign _446 = _445[30:0];
    assign _448 = { _446,
                    _447 };
    assign _449 = _448 < _403;
    assign _450 = ~ _449;
    assign _438 = _74[27:27];
    assign _435 = _430 - _403;
    assign _436 = _432 ? _435 : _430;
    assign _437 = _436[30:0];
    assign _439 = { _437,
                    _438 };
    assign _440 = _439 < _403;
    assign _441 = ~ _440;
    assign _429 = _74[28:28];
    assign _426 = _421 - _403;
    assign _427 = _423 ? _426 : _421;
    assign _428 = _427[30:0];
    assign _430 = { _428,
                    _429 };
    assign _431 = _430 < _403;
    assign _432 = ~ _431;
    assign _420 = _74[29:29];
    assign _417 = _412 - _403;
    assign _418 = _414 ? _417 : _412;
    assign _419 = _418[30:0];
    assign _421 = { _419,
                    _420 };
    assign _422 = _421 < _403;
    assign _423 = ~ _422;
    assign _411 = _74[30:30];
    assign _408 = _402 - _403;
    assign _409 = _405 ? _408 : _402;
    assign _410 = _409[30:0];
    assign _412 = { _410,
                    _411 };
    assign _413 = _412 < _403;
    assign _414 = ~ _413;
    assign _403 = 32'b00000000000000000000000000000011;
    assign _48 = 3'b001;
    assign _49 = _28 == _48;
    assign _69 = ~ _39;
    assign _70 = _34 & _69;
    assign _71 = _70 & _49;
    assign _75 = _71 ? _6 : _74;
    assign _77 = _22 ? _58 : _75;
    assign _4 = _77;
    always @(posedge _16) begin
        if (_14)
            _74 <= _58;
        else
            _74 <= _4;
    end
    assign _401 = _74[31:31];
    assign _400 = 31'b0000000000000000000000000000000;
    assign _402 = { _400,
                    _401 };
    assign _404 = _402 < _403;
    assign _405 = ~ _404;
    assign _406 = { _400,
                    _405 };
    assign _407 = _406[30:0];
    assign _415 = { _407,
                    _414 };
    assign _416 = _415[30:0];
    assign _424 = { _416,
                    _423 };
    assign _425 = _424[30:0];
    assign _433 = { _425,
                    _432 };
    assign _434 = _433[30:0];
    assign _442 = { _434,
                    _441 };
    assign _443 = _442[30:0];
    assign _451 = { _443,
                    _450 };
    assign _452 = _451[30:0];
    assign _460 = { _452,
                    _459 };
    assign _461 = _460[30:0];
    assign _469 = { _461,
                    _468 };
    assign _470 = _469[30:0];
    assign _478 = { _470,
                    _477 };
    assign _479 = _478[30:0];
    assign _487 = { _479,
                    _486 };
    assign _488 = _487[30:0];
    assign _496 = { _488,
                    _495 };
    assign _497 = _496[30:0];
    assign _505 = { _497,
                    _504 };
    assign _506 = _505[30:0];
    assign _514 = { _506,
                    _513 };
    assign _515 = _514[30:0];
    assign _523 = { _515,
                    _522 };
    assign _524 = _523[30:0];
    assign _532 = { _524,
                    _531 };
    assign _533 = _532[30:0];
    assign _541 = { _533,
                    _540 };
    assign _542 = _541[30:0];
    assign _550 = { _542,
                    _549 };
    assign _551 = _550[30:0];
    assign _559 = { _551,
                    _558 };
    assign _560 = _559[30:0];
    assign _568 = { _560,
                    _567 };
    assign _569 = _568[30:0];
    assign _577 = { _569,
                    _576 };
    assign _578 = _577[30:0];
    assign _586 = { _578,
                    _585 };
    assign _587 = _586[30:0];
    assign _595 = { _587,
                    _594 };
    assign _596 = _595[30:0];
    assign _604 = { _596,
                    _603 };
    assign _605 = _604[30:0];
    assign _613 = { _605,
                    _612 };
    assign _614 = _613[30:0];
    assign _622 = { _614,
                    _621 };
    assign _623 = _622[30:0];
    assign _631 = { _623,
                    _630 };
    assign _632 = _631[30:0];
    assign _640 = { _632,
                    _639 };
    assign _641 = _640[30:0];
    assign _649 = { _641,
                    _648 };
    assign _650 = _649[30:0];
    assign _658 = { _650,
                    _657 };
    assign _659 = _658[30:0];
    assign _667 = { _659,
                    _666 };
    assign _668 = _667[30:0];
    assign _676 = { _668,
                    _675 };
    assign _677 = _676[30:0];
    assign _685 = { _677,
                    _684 };
    assign _686 = { _58,
                    _685 };
    assign _392 = _83[0:0];
    assign _389 = _384 - _403;
    assign _390 = _386 ? _389 : _384;
    assign _391 = _390[30:0];
    assign _393 = { _391,
                    _392 };
    assign _394 = _393 < _403;
    assign _395 = ~ _394;
    assign _383 = _83[1:1];
    assign _380 = _375 - _403;
    assign _381 = _377 ? _380 : _375;
    assign _382 = _381[30:0];
    assign _384 = { _382,
                    _383 };
    assign _385 = _384 < _403;
    assign _386 = ~ _385;
    assign _374 = _83[2:2];
    assign _371 = _366 - _403;
    assign _372 = _368 ? _371 : _366;
    assign _373 = _372[30:0];
    assign _375 = { _373,
                    _374 };
    assign _376 = _375 < _403;
    assign _377 = ~ _376;
    assign _365 = _83[3:3];
    assign _362 = _357 - _403;
    assign _363 = _359 ? _362 : _357;
    assign _364 = _363[30:0];
    assign _366 = { _364,
                    _365 };
    assign _367 = _366 < _403;
    assign _368 = ~ _367;
    assign _356 = _83[4:4];
    assign _353 = _348 - _403;
    assign _354 = _350 ? _353 : _348;
    assign _355 = _354[30:0];
    assign _357 = { _355,
                    _356 };
    assign _358 = _357 < _403;
    assign _359 = ~ _358;
    assign _347 = _83[5:5];
    assign _344 = _339 - _403;
    assign _345 = _341 ? _344 : _339;
    assign _346 = _345[30:0];
    assign _348 = { _346,
                    _347 };
    assign _349 = _348 < _403;
    assign _350 = ~ _349;
    assign _338 = _83[6:6];
    assign _335 = _330 - _403;
    assign _336 = _332 ? _335 : _330;
    assign _337 = _336[30:0];
    assign _339 = { _337,
                    _338 };
    assign _340 = _339 < _403;
    assign _341 = ~ _340;
    assign _329 = _83[7:7];
    assign _326 = _321 - _403;
    assign _327 = _323 ? _326 : _321;
    assign _328 = _327[30:0];
    assign _330 = { _328,
                    _329 };
    assign _331 = _330 < _403;
    assign _332 = ~ _331;
    assign _320 = _83[8:8];
    assign _317 = _312 - _403;
    assign _318 = _314 ? _317 : _312;
    assign _319 = _318[30:0];
    assign _321 = { _319,
                    _320 };
    assign _322 = _321 < _403;
    assign _323 = ~ _322;
    assign _311 = _83[9:9];
    assign _308 = _303 - _403;
    assign _309 = _305 ? _308 : _303;
    assign _310 = _309[30:0];
    assign _312 = { _310,
                    _311 };
    assign _313 = _312 < _403;
    assign _314 = ~ _313;
    assign _302 = _83[10:10];
    assign _299 = _294 - _403;
    assign _300 = _296 ? _299 : _294;
    assign _301 = _300[30:0];
    assign _303 = { _301,
                    _302 };
    assign _304 = _303 < _403;
    assign _305 = ~ _304;
    assign _293 = _83[11:11];
    assign _290 = _285 - _403;
    assign _291 = _287 ? _290 : _285;
    assign _292 = _291[30:0];
    assign _294 = { _292,
                    _293 };
    assign _295 = _294 < _403;
    assign _296 = ~ _295;
    assign _284 = _83[12:12];
    assign _281 = _276 - _403;
    assign _282 = _278 ? _281 : _276;
    assign _283 = _282[30:0];
    assign _285 = { _283,
                    _284 };
    assign _286 = _285 < _403;
    assign _287 = ~ _286;
    assign _275 = _83[13:13];
    assign _272 = _267 - _403;
    assign _273 = _269 ? _272 : _267;
    assign _274 = _273[30:0];
    assign _276 = { _274,
                    _275 };
    assign _277 = _276 < _403;
    assign _278 = ~ _277;
    assign _266 = _83[14:14];
    assign _263 = _258 - _403;
    assign _264 = _260 ? _263 : _258;
    assign _265 = _264[30:0];
    assign _267 = { _265,
                    _266 };
    assign _268 = _267 < _403;
    assign _269 = ~ _268;
    assign _257 = _83[15:15];
    assign _254 = _249 - _403;
    assign _255 = _251 ? _254 : _249;
    assign _256 = _255[30:0];
    assign _258 = { _256,
                    _257 };
    assign _259 = _258 < _403;
    assign _260 = ~ _259;
    assign _248 = _83[16:16];
    assign _245 = _240 - _403;
    assign _246 = _242 ? _245 : _240;
    assign _247 = _246[30:0];
    assign _249 = { _247,
                    _248 };
    assign _250 = _249 < _403;
    assign _251 = ~ _250;
    assign _239 = _83[17:17];
    assign _236 = _231 - _403;
    assign _237 = _233 ? _236 : _231;
    assign _238 = _237[30:0];
    assign _240 = { _238,
                    _239 };
    assign _241 = _240 < _403;
    assign _242 = ~ _241;
    assign _230 = _83[18:18];
    assign _227 = _222 - _403;
    assign _228 = _224 ? _227 : _222;
    assign _229 = _228[30:0];
    assign _231 = { _229,
                    _230 };
    assign _232 = _231 < _403;
    assign _233 = ~ _232;
    assign _221 = _83[19:19];
    assign _218 = _213 - _403;
    assign _219 = _215 ? _218 : _213;
    assign _220 = _219[30:0];
    assign _222 = { _220,
                    _221 };
    assign _223 = _222 < _403;
    assign _224 = ~ _223;
    assign _212 = _83[20:20];
    assign _209 = _204 - _403;
    assign _210 = _206 ? _209 : _204;
    assign _211 = _210[30:0];
    assign _213 = { _211,
                    _212 };
    assign _214 = _213 < _403;
    assign _215 = ~ _214;
    assign _203 = _83[21:21];
    assign _200 = _195 - _403;
    assign _201 = _197 ? _200 : _195;
    assign _202 = _201[30:0];
    assign _204 = { _202,
                    _203 };
    assign _205 = _204 < _403;
    assign _206 = ~ _205;
    assign _194 = _83[22:22];
    assign _191 = _186 - _403;
    assign _192 = _188 ? _191 : _186;
    assign _193 = _192[30:0];
    assign _195 = { _193,
                    _194 };
    assign _196 = _195 < _403;
    assign _197 = ~ _196;
    assign _185 = _83[23:23];
    assign _182 = _177 - _403;
    assign _183 = _179 ? _182 : _177;
    assign _184 = _183[30:0];
    assign _186 = { _184,
                    _185 };
    assign _187 = _186 < _403;
    assign _188 = ~ _187;
    assign _176 = _83[24:24];
    assign _173 = _168 - _403;
    assign _174 = _170 ? _173 : _168;
    assign _175 = _174[30:0];
    assign _177 = { _175,
                    _176 };
    assign _178 = _177 < _403;
    assign _179 = ~ _178;
    assign _167 = _83[25:25];
    assign _164 = _159 - _403;
    assign _165 = _161 ? _164 : _159;
    assign _166 = _165[30:0];
    assign _168 = { _166,
                    _167 };
    assign _169 = _168 < _403;
    assign _170 = ~ _169;
    assign _158 = _83[26:26];
    assign _155 = _150 - _403;
    assign _156 = _152 ? _155 : _150;
    assign _157 = _156[30:0];
    assign _159 = { _157,
                    _158 };
    assign _160 = _159 < _403;
    assign _161 = ~ _160;
    assign _149 = _83[27:27];
    assign _146 = _141 - _403;
    assign _147 = _143 ? _146 : _141;
    assign _148 = _147[30:0];
    assign _150 = { _148,
                    _149 };
    assign _151 = _150 < _403;
    assign _152 = ~ _151;
    assign _140 = _83[28:28];
    assign _137 = _132 - _403;
    assign _138 = _134 ? _137 : _132;
    assign _139 = _138[30:0];
    assign _141 = { _139,
                    _140 };
    assign _142 = _141 < _403;
    assign _143 = ~ _142;
    assign _131 = _83[29:29];
    assign _128 = _123 - _403;
    assign _129 = _125 ? _128 : _123;
    assign _130 = _129[30:0];
    assign _132 = { _130,
                    _131 };
    assign _133 = _132 < _403;
    assign _134 = ~ _133;
    assign _122 = _83[30:30];
    assign _119 = _113 - _403;
    assign _120 = _116 ? _119 : _113;
    assign _121 = _120[30:0];
    assign _123 = { _121,
                    _122 };
    assign _124 = _123 < _403;
    assign _125 = ~ _124;
    assign _6 = num;
    assign _43 = 3'b000;
    assign _44 = _28 == _43;
    assign _78 = ~ _39;
    assign _79 = _34 & _78;
    assign _80 = _79 & _44;
    assign _84 = _80 ? _6 : _83;
    assign _86 = _22 ? _58 : _84;
    assign _7 = _86;
    always @(posedge _16) begin
        if (_14)
            _83 <= _58;
        else
            _83 <= _7;
    end
    assign _112 = _83[31:31];
    assign _113 = { _400,
                    _112 };
    assign _115 = _113 < _403;
    assign _116 = ~ _115;
    assign _117 = { _400,
                    _116 };
    assign _118 = _117[30:0];
    assign _126 = { _118,
                    _125 };
    assign _127 = _126[30:0];
    assign _135 = { _127,
                    _134 };
    assign _136 = _135[30:0];
    assign _144 = { _136,
                    _143 };
    assign _145 = _144[30:0];
    assign _153 = { _145,
                    _152 };
    assign _154 = _153[30:0];
    assign _162 = { _154,
                    _161 };
    assign _163 = _162[30:0];
    assign _171 = { _163,
                    _170 };
    assign _172 = _171[30:0];
    assign _180 = { _172,
                    _179 };
    assign _181 = _180[30:0];
    assign _189 = { _181,
                    _188 };
    assign _190 = _189[30:0];
    assign _198 = { _190,
                    _197 };
    assign _199 = _198[30:0];
    assign _207 = { _199,
                    _206 };
    assign _208 = _207[30:0];
    assign _216 = { _208,
                    _215 };
    assign _217 = _216[30:0];
    assign _225 = { _217,
                    _224 };
    assign _226 = _225[30:0];
    assign _234 = { _226,
                    _233 };
    assign _235 = _234[30:0];
    assign _243 = { _235,
                    _242 };
    assign _244 = _243[30:0];
    assign _252 = { _244,
                    _251 };
    assign _253 = _252[30:0];
    assign _261 = { _253,
                    _260 };
    assign _262 = _261[30:0];
    assign _270 = { _262,
                    _269 };
    assign _271 = _270[30:0];
    assign _279 = { _271,
                    _278 };
    assign _280 = _279[30:0];
    assign _288 = { _280,
                    _287 };
    assign _289 = _288[30:0];
    assign _297 = { _289,
                    _296 };
    assign _298 = _297[30:0];
    assign _306 = { _298,
                    _305 };
    assign _307 = _306[30:0];
    assign _315 = { _307,
                    _314 };
    assign _316 = _315[30:0];
    assign _324 = { _316,
                    _323 };
    assign _325 = _324[30:0];
    assign _333 = { _325,
                    _332 };
    assign _334 = _333[30:0];
    assign _342 = { _334,
                    _341 };
    assign _343 = _342[30:0];
    assign _351 = { _343,
                    _350 };
    assign _352 = _351[30:0];
    assign _360 = { _352,
                    _359 };
    assign _361 = _360[30:0];
    assign _369 = { _361,
                    _368 };
    assign _370 = _369[30:0];
    assign _378 = { _370,
                    _377 };
    assign _379 = _378[30:0];
    assign _387 = { _379,
                    _386 };
    assign _388 = _387[30:0];
    assign _396 = { _388,
                    _395 };
    assign _397 = { _58,
                    _396 };
    assign _687 = _397 * _686;
    assign _688 = _687[63:0];
    assign _691 = _688 < _690;
    assign _692 = ~ _691;
    assign _695 = _692 ? _694 : _29;
    assign _696 = _108 + _695;
    assign _94 = 3'b111;
    assign _98 = _28 + _48;
    assign _99 = _34 ? _98 : _28;
    assign _101 = _96 ? _43 : _99;
    assign _38 = 3'b110;
    assign _89 = _37 + _48;
    assign _87 = _34 & _39;
    assign _90 = _87 ? _89 : _37;
    assign _92 = _22 ? _43 : _90;
    assign _8 = _92;
    always @(posedge _16) begin
        if (_14)
            _37 <= _43;
        else
            _37 <= _8;
    end
    assign _39 = _37 < _38;
    assign _93 = _34 & _39;
    assign _103 = _93 ? _43 : _101;
    assign _105 = _22 ? _43 : _103;
    assign _9 = _105;
    always @(posedge _16) begin
        if (_14)
            _28 <= _43;
        else
            _28 <= _9;
    end
    assign _95 = _28 == _94;
    assign _96 = _34 & _95;
    assign _697 = _96 ? _696 : _108;
    assign _699 = _22 ? _29 : _697;
    assign _10 = _699;
    always @(posedge _16) begin
        if (_14)
            _108 <= _29;
        else
            _108 <= _10;
    end
    assign _31 = 1'b0;
    assign _14 = clear;
    assign _16 = clock;
    assign vdd = 1'b1;
    assign _18 = num_last;
    assign _20 = num_valid;
    assign _34 = _33 & _20;
    assign _700 = _34 & _18;
    assign _701 = _700 ? vdd : _32;
    assign _22 = load;
    assign _703 = _22 ? _31 : _701;
    assign _23 = _703;
    always @(posedge _16) begin
        if (_14)
            _32 <= _31;
        else
            _32 <= _23;
    end
    assign _33 = ~ _32;
    assign ready = _33;
    assign done_ = _32;
    assign part1_result = _108;
    assign part2_result = _29;
    assign idx_mod8 = _28;

endmodule
