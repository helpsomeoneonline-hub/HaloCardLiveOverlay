from pathlib import Path

src = Path("app/src/main/java/com/byso/halocardoverlay/DashboardAccessibilityService.kt")
s = src.read_text(encoding="utf-8")
def change(old, new, title):
    global s
    if old not in s:
        raise SystemExit("v1.8 source mismatch: " + title)
    s = s.replace(old, new, 1)

change('''        "mozac_browser_toolbar_url", "url_text", "url_field", "address_bar"
''', '''        "mozac_browser_toolbar_url", "url_text", "url_field", "address_bar",
        "mozac_browser_toolbar", "browser_toolbar_url", "toolbar_text",
        "mozac_browser_toolbar_display_url", "mozac_browser_toolbar_url_text"
''', "address identifiers")
change('''            flags = flags or AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS
''', '''            flags = flags or AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or
                AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS
''', "Firefox toolbar accessibility visibility")
change('''    @Volatile private var tabTransitionUntil = 0L
''', '''    @Volatile private var tabTransitionUntil = 0L
    private var lastFirefoxProbe = 0L
''', "Firefox private diagnostic interval")
change('''            while (queue.isNotEmpty() && visited < 420 &&
                   SystemClock.elapsedRealtime() - start < 110L) {''', '''            // GeckoView may expose toolbar elements later than Chrome.
            // This scan runs on a dedicated worker, not Android's UI thread.
            val maximumNodes = if (isFirefox) 1100 else 420
            val maximumMs = if (isFirefox) 460L else 170L
            while (queue.isNotEmpty() && visited < maximumNodes &&
                   SystemClock.elapsedRealtime() - start < maximumMs) {''', "Firefox bounded scan")
change('''                    if (isAddressNode(node, id)) {
                        if (dashboardUrl.containsMatchIn(content) || dashboardUrl.containsMatchIn(description)) urlsFound = true
                        if (dashboardHost.containsMatchIn(content) || dashboardHost.containsMatchIn(description)) hostFound = true
                    }
                    for (i in 0 until node.childCount) {''', '''                    if (isAddressNode(node, id)) {
                        if (dashboardUrl.containsMatchIn(content) || dashboardUrl.containsMatchIn(description)) urlsFound = true
                        if (dashboardHost.containsMatchIn(content) || dashboardHost.containsMatchIn(description)) hostFound = true
                    }
                    if (urlsFound) break
                    for (i in 0 until node.childCount) {''', "early exit on verified address")
change('''            if (tabTrayOpen) {
''', '''            if (isFirefox && SystemClock.elapsedRealtime() - lastFirefoxProbe > 10000L) {
                lastFirefoxProbe = SystemClock.elapsedRealtime()
                Diagnostics.record(this, "Firefox probe",
                    "nodes=$visited timedMs=${SystemClock.elapsedRealtime() - start} " +
                    "fullPath=$urlsFound host=$hostFound labels=$dashboardText/$cardsText tabTray=$tabTrayOpen")
            }
            if (tabTrayOpen) {
''', "privacy-safe probe counters")
change('''        if (addressIds.any { key -> last == key || last.startsWith("${key}_") || last.endsWith("_${key}") }) return true
''', '''        if (addressIds.any { key -> last == key || last.startsWith("${key}_") || last.endsWith("_${key}") }) return true
        if (last.contains("browser_toolbar") &&
            (last.contains("url") || last.contains("display") || last.contains("location"))) return true
''', "variant Firefox toolbar view identifiers")
change('''                if (parentId.contains("browser_toolbar") || parentId.contains("toolbar_layout")) return true
''', '''                if (parentId.contains("browser_toolbar") || parentId.contains("toolbar_layout") ||
                    parentId.contains("toolbar_container") || parentId.contains("navigation_toolbar")) return true
''', "variant Firefox toolbar parents")
src.write_text(s, encoding="utf-8")

gradle = Path("app/build.gradle.kts")
g = gradle.read_text(encoding="utf-8")
if 'versionCode = 8' not in g or 'versionName = "1.7"' not in g:
    raise SystemExit("Expected v1.7 version before update")
gradle.write_text(g.replace("versionCode = 8", "versionCode = 9", 1).replace('versionName = "1.7"', 'versionName = "1.8"', 1), encoding="utf-8")

log = Path("app/src/main/java/com/byso/halocardoverlay/Diagnostics.kt")
d = log.read_text(encoding="utf-8")
if "App: 1.6 / versionCode 7" not in d:
    raise SystemExit("Expected diagnostic version string")
log.write_text(d.replace("App: 1.6 / versionCode 7", "App: 1.8 / versionCode 9", 1), encoding="utf-8")
print("HaloCard v1.8 Firefox address detection updated")
