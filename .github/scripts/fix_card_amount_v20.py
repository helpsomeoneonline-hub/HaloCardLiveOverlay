from pathlib import Path

root = Path("app/src/main/java/com/byso/halocardoverlay")
parser = root / "CardBalanceParser.kt"
code = parser.read_text(encoding="utf-8")

before = """            if (limit.signum() <= 0 || spent.signum() < 0) null
            else BalanceAmounts(spent, limit)"""
after = """            // OCR sometimes reads '$756' as '$7'. Never display a fabricated
            // negative result when the recognized limit is below the amount spent.
            // The user sees 'Verifying' until a complete, valid limit is read.
            if (limit.signum() <= 0 || spent.signum() < 0 || spent > limit) null
            else BalanceAmounts(spent, limit)"""
if before not in code:
    raise SystemExit("Expected current CardBalanceParser code not found")
parser.write_text(code.replace(before, after, 1), encoding="utf-8")

service = root / "BalanceCaptureService.kt"
s = service.read_text(encoding="utf-8")
def change(old, new, context):
    global s
    if old not in s:
        raise SystemExit(f"v2.0 source mismatch: {context}")
    s = s.replace(old, new, 1)

change("""    private var consecutiveMisses = 0
    private var firefoxMatches = 0""",
"""    private var consecutiveMisses = 0
    // Confirm values on two independent OCR frames before publishing.
    // Reduces false balances caused by transient font/animation misreads.
    private var pendingBalance: BalanceAmounts? = null
    private var repeatedBalanceFrames = 0
    private var publishedBalance: BalanceAmounts? = null

    private fun sameAmounts(a: BalanceAmounts?, b: BalanceAmounts): Boolean =
        a != null && a.spent.compareTo(b.spent) == 0 && a.limit.compareTo(b.limit) == 0

    private var firefoxMatches = 0""", "balance confirmation state")

change("""                consecutiveMisses = 0
                showStatus("Scanning…", "Reading current HaloCard card")""",
"""                consecutiveMisses = 0
                pendingBalance = null
                repeatedBalanceFrames = 0
                publishedBalance = null
                showStatus("Scanning…", "Reading current HaloCard card")""", "clear old balance on returning dashboard")

change("""                if (match != null) {
                    if (consecutiveMisses > 2) Diagnostics.record(this, "OCR", "Card balance recognized after previous misses")
                    consecutiveMisses = 0
                    showBalance(match)
                } else {
                    consecutiveMisses++
                    if (consecutiveMisses == 3) {
                        Diagnostics.record(this, "OCR", "Three captures without a matching card amount")
                        showStatus("—", "Waiting for 'spent of limit' on screen")
                    }
                }""",
"""                if (match != null) {
                    if (consecutiveMisses > 2) Diagnostics.record(this, "OCR", "Card balance recognized after previous misses")
                    consecutiveMisses = 0
                    if (sameAmounts(pendingBalance, match)) {
                        repeatedBalanceFrames++
                    } else {
                        pendingBalance = match
                        repeatedBalanceFrames = 1
                        // Clear stale figures immediately while verifying another card.
                        if (!sameAmounts(publishedBalance, match)) {
                            showStatus("Verifying…", "Confirming current card figures")
                        }
                    }
                    if (repeatedBalanceFrames >= 2 && !sameAmounts(publishedBalance, match)) {
                        publishedBalance = match
                        showBalance(match)
                    }
                } else {
                    consecutiveMisses++
                    pendingBalance = null
                    repeatedBalanceFrames = 0
                    if (consecutiveMisses == 3) {
                        publishedBalance = null
                        Diagnostics.record(this, "OCR", "Three captures without a matching reliable card amount")
                        showStatus("—", "Waiting for a clear 'spent of limit' reading")
                    }
                }""", "validate OCR across two independent frames")
change("""                consecutiveMisses++
                if (consecutiveMisses == 3) {
                    Diagnostics.record(this, "OCR", "Text recognition failed three times")""",
"""                consecutiveMisses++
                pendingBalance = null
                repeatedBalanceFrames = 0
                if (consecutiveMisses == 3) {
                    publishedBalance = null
                    Diagnostics.record(this, "OCR", "Text recognition failed three times")""", "reset after OCR failure")

service.write_text(s, encoding="utf-8")

gradle = Path("app/build.gradle.kts")
g = gradle.read_text(encoding="utf-8")
assert 'versionCode = 10' in g and 'versionName = "1.9"' in g, "expected v1.9 base"
gradle.write_text(g.replace('versionCode = 10', 'versionCode = 11', 1)
                   .replace('versionName = "1.9"', 'versionName = "2.0"', 1), encoding="utf-8")

# UI now distinguishes verified results from OCR misreads; don't store figures in diagnostics.
print("Installed v2.0 OCR validation, consecutive-frame confirmation, and stable signing version bump.")
