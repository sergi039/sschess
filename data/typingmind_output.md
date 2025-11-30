# 🎯 Chess Game Analysis

## 📋 Game Information

**sergioquesadas (739) vs pommy-lad (774)**
**Result:** ½-½ - Draw

## 📊 Computer Analysis

| Metric | Value | Rating |
|--------|-------|--------|
| **Accuracy** | 20.5% | 🔴 Need improvement |
| **Blunders** | 20 | 🔴 |
| **Mistakes** | 11 | 🔴 |
| **Inaccuracies** | 6 | 🟡 |

## 🎮 Interactive Board


<div id="board-146092379714" style="width: 100%; max-width: 800px; margin: 20px auto;"></div>
<link rel="stylesheet" href="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.css">
<script src="https://unpkg.com/lichess-pgn-viewer@2.1.0/dist/lichess-pgn-viewer.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const pgn = `[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.11.29"]
[Round "-"]
[White "sergioquesadas"]
[Black "pommy-lad"]
[Result "0-1"]
[CurrentPosition "2k4r/ppp3p1/2n5/4p1p1/1P2n1P1/2P2N1P/P5K1/RN1r4 w - - 2 20"]
[Timezone "UTC"]
[ECO "C41"]
[ECOUrl "https://www.chess.com/openings/Philidor-Defense-3.Bc4"]
[UTCDate "2025.11.29"]
[UTCTime "07:18:10"]
[WhiteElo "739"]
[BlackElo "774"]
[TimeControl "600"]
[Termination "pommy-lad won by resignation"]
[StartTime "07:18:10"]
[EndDate "2025.11.29"]
[EndTime "07:24:30"]
[Link "https://www.chess.com/game/live/146092379714"]

1. e4 {[%clk 0:09:59.1]} 1... e5 {[%clk 0:09:58]} 2. Nf3 {[%clk 0:09:58.1]} 2... d6 {[%clk 0:09:55.4]} 3. Bc4 {[%clk 0:09:55.2]} 3... h6 {[%clk 0:09:52.4]} 4. c3 {[%clk 0:09:53.5]} 4... Nc6 {[%clk 0:09:49.9]} 5. Qb3 {[%clk 0:09:51.9]} 5... Be6 {[%clk 0:09:32.9]} 6. Bxe6 {[%clk 0:09:26.2]} 6... fxe6 {[%clk 0:09:29]} 7. Qxe6+ {[%clk 0:09:24.6]} 7... Be7 {[%clk 0:09:13.5]} 8. d4 {[%clk 0:09:14.5]} 8... Nf6 {[%clk 0:09:02.8]} 9. dxe5 {[%clk 0:08:51.8]} 9... dxe5 {[%clk 0:08:37]} 10. O-O {[%clk 0:08:34]} 10... Qd7 {[%clk 0:08:17.9]} 11. Qxd7+ {[%clk 0:08:06.1]} 11... Nxd7 {[%clk 0:08:15.5]} 12. Be3 {[%clk 0:07:54.6]} 12... O-O-O {[%clk 0:08:10.9]} 13. Rd1 {[%clk 0:07:50]} 13... Nf6 {[%clk 0:07:59]} 14. h3 {[%clk 0:07:45]} 14... Rxd1+ {[%clk 0:07:54.1]} 15. Kh2 {[%clk 0:07:41]} 15... Nxe4 {[%clk 0:07:50.8]} 16. b4 {[%clk 0:06:49.7]} 16... Bg5 {[%clk 0:07:46.3]} 17. Bxg5 {[%clk 0:06:35.8]} 17... hxg5 {[%clk 0:07:42.1]} 18. g4 {[%clk 0:06:31.1]} 18... Nxf2 {[%clk 0:07:35.6]} 19. Kg2 {[%clk 0:06:29.8]} 19... Ne4 {[%clk 0:07:27.9]} 0-1
`;
    LichessPgnViewer(document.getElementById('board-146092379714'), {
        pgn: pgn,
        orientation: 'white',
        showMoves: 'right',
        showClocks: false,
        drawArrows: true,
        viewOnly: false,
        coordinates: true,
        menu: {
            getPgn: false,
            practise: false,
            analysisBoard: false
        }
    });
});
</script>


## 📝 Key Moments

### Biggest Mistakes:

**Move 3. h7h6 ?**
- Lost 1.2 pawns of advantage
- Better was: f8e7

**Move 4. c2c3 ?**
- Lost 1.3 pawns of advantage
- Better was: d2d4

**Move 5. c8e6 ?**
- Lost 1.9 pawns of advantage
- Better was: d8d7

**Move 6. c4e6 ??**
- Lost 3.9 pawns of advantage

**Move 6. f7e6 ??**
- Lost 3.8 pawns of advantage


## 🔗 Links

- [View original game on Chess.com](https://www.chess.com/game/live/146092379714)
- Game analyzed with Stockfish engine

---
*Use arrow keys or click moves to navigate through the game*
