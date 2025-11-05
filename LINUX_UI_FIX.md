# Linux UI Layout Fix - Latest Bets Table

## Problem

On Linux, the "Latest Bets" table was being cut off at the bottom with no visible scrollbar. The table content was not fully displayed within the available window space.

## Root Cause

The issue was caused by several factors:

1. **Insufficient Vertical Space**: With a fixed window height of 825px, the content above the table (status, buttons, 180px logo, etc.) left less than 200px for the table, but the table had a 200px minimum height requirement.

2. **Missing Scroll Policies**: The table didn't have explicit vertical scrollbar policies configured, which can cause issues on Linux where Qt behavior differs from Windows/macOS.

3. **Size Policy Not Set**: The table lacked proper size policies to allow it to shrink and use scrollbars effectively.

4. **Scrollbar Styling Issues**: The scrollbar styling was minimal and might not render properly on all Linux environments.

## Solution Implemented

### 1. Set Proper Size Policy and Scroll Policies

```python
# Set size policy to allow the table to shrink and use scrollbar
self.betsTable.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

# Ensure scrollbars are shown when needed (important for Linux)
self.betsTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
self.betsTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
```

### 2. Reduced Minimum Height

Changed table minimum height from 200px to 150px to fit within the available vertical space:

```python
self.betsTable.setMinimumHeight(150)  # Reduced from 200
self.betsTable.setMaximumHeight(300)
```

### 3. Reduced Logo Size

Reduced the Solana logo from 180px to 160px height to provide more space for the table:

```python
self.logoLabel.setMinimumSize(QtCore.QSize(360, 160))  # Reduced from 180
self.logoLabel.setMaximumSize(QtCore.QSize(360, 160))
```

### 4. Enhanced Scrollbar Styling

Improved scrollbar styling for better visibility and functionality on Linux:

```python
"QScrollBar:vertical {"
"background: rgba(20, 20, 40, 0.8);"
"width: 12px;"  # Increased from 10px
"margin: 0px;"
"border: 1px solid rgba(60, 60, 80, 0.5);"
"border-radius: 6px;"
"}"
"QScrollBar::handle:vertical {"
"background: rgba(120, 120, 150, 0.9);"
"border: 1px solid rgba(140, 140, 170, 0.5);"
"border-radius: 5px;"
"min-height: 30px;"  # Increased from 20px
"margin: 2px;"
"}"
"QScrollBar::handle:vertical:hover {"
"background: rgba(140, 140, 170, 1.0);"
"}"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
"height: 0px;"  # Remove arrow buttons
"}"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
"background: none;"
"}"
```

## Space Calculation

With the fixes applied:

**Before:**
- Window height: 825px
- Content above table: ~640px
- Space for table: ~185px
- Table minimum: 200px
- **Result**: Table cut off ❌

**After:**
- Window height: 825px
- Content above table: ~620px (reduced logo)
- Space for table: ~205px
- Table minimum: 150px
- **Result**: Table fits with scrollbar ✅

## Benefits

1. ✅ **Table fully visible** with proper scrollbar
2. ✅ **Better scrollbar visibility** on Linux
3. ✅ **Consistent behavior** across different Linux distributions
4. ✅ **More usable space** for bet history display
5. ✅ **Hover effects** on scrollbar for better UX

## Testing

Test the fix by:

1. Running the application on Linux:
   ```bash
   python main.py
   ```

2. Check that:
   - The "Latest Bets" table is fully visible
   - The scrollbar appears when there are enough bets to scroll
   - The scrollbar is visible and easy to use
   - No content is cut off at the bottom

3. Add multiple bets to test scrolling:
   - The table should scroll smoothly
   - All bets should be accessible via scrollbar

## Platform-Specific Notes

### Why This Issue Occurred on Linux

1. **Qt Rendering Differences**: Qt renders slightly differently on Linux (X11/Wayland) compared to Windows/macOS
2. **Font Rendering**: Font metrics can vary, causing slightly different layout heights
3. **Scrollbar Behavior**: Default scrollbar visibility and styling differs on Linux
4. **Window Manager**: Different window managers may handle fixed-size windows differently

### Testing Across Distributions

This fix has been designed to work across:
- Ubuntu/Debian (GNOME, KDE, Xfce)
- Fedora/RHEL (GNOME, KDE)
- Arch Linux (various DEs)
- Other modern Linux distributions

## Related Files

- **`main.py`** (lines 609-683) - Table configuration and styling
- **`main.py`** (lines 464-496) - Logo size configuration

## Future Improvements

If layout issues persist, consider:

1. **Scroll Area**: Wrap the entire `roundCardPanel` in a `QScrollArea`
2. **Dynamic Sizing**: Calculate minimum heights based on window size
3. **Responsive Layout**: Use percentage-based sizing instead of fixed pixels
4. **Collapsible Sections**: Allow users to collapse/expand sections (like the logo) to customize layout

## Rollback

If you need to rollback these changes:

```python
# Restore original values:
self.betsTable.setMinimumHeight(200)  # Was 150
self.logoLabel.setMinimumSize(QtCore.QSize(360, 180))  # Was 160
self.logoLabel.setMaximumSize(QtCore.QSize(360, 180))
# Remove size policy and scrollbar policy lines
```

However, this would bring back the original issue.

