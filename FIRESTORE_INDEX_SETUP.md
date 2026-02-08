# Firestore Index Setup

## Error: "The query requires an index"

If you see this error when loading the Reports page, you need to create a composite index.

### Quick Fix (Recommended):
1. **Click the link in the error message** - Firebase will auto-create the index
2. Wait 1-2 minutes for the index to build
3. Refresh the Reports page

### Manual Fix:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to **Firestore Database** → **Indexes** tab
4. Click **Create Index**
5. Configure:
   - **Collection ID**: `reports`
   - **Fields to index**:
     - Field: `netScore`, Order: `Descending`
     - Field: `timestamp`, Order: `Descending`
   - **Query scope**: Collection
6. Click **Create**
7. Wait for the index to build (shows status in console)

---

## Alternative: Simplified Query (No Index Needed)

If you want to avoid creating an index, I've updated `reportsService.js` to use only `netScore` for sorting. This works immediately without any index configuration.

The timestamp will still be visible, just not used for sorting.
