# 📸 Long Receipt Support Guide

## Problem Solved

**Before:** Couldn't capture receipts with 100+ line items (like Aldi shopping trips)  
**After:** Multi-photo support with smart merging ✅

---

## 🎯 How to Capture Long Receipts

### Option 1: Multi-Photo Capture (Recommended)

1. **Take photo of TOP half**
   - Capture store name, date, first ~30 items
   - Click ➕ "Add Another Photo"

2. **Take photo of MIDDLE section**
   - Capture next ~30-40 items
   - Click ➕ "Add Another Photo" (if needed)

3. **Take photo of BOTTOM half**
   - Capture last items, total, payment info
   - Click ✅ "Process Receipt"

4. **Backend automatically merges**
   - All items combined
   - Duplicates removed
   - Single receipt entry

---

### Option 2: Step Back & Zoom

1. **Step back 2-3 meters** from receipt
2. **Hold phone horizontally** (landscape mode)
3. **Ensure good lighting**
4. **Capture in one shot**

---

### Option 3: Accordion Fold

1. **Fold receipt** accordion-style (zig-zag)
2. **Lay flat** on table
3. **Take photo** from above
4. **Capture all sections** visible

---

## 💡 Tips Shown in App

Click "💡 Tips for Long Receipts" in the camera view to see:

- ✓ Step back 2-3 meters from receipt
- ✓ Hold phone horizontally (landscape)
- ✓ For very long receipts: capture top half, then bottom half
- ✓ Or fold receipt accordion-style

---

## 🎨 UI Features

### Photo Collection

- **Counter**: Shows "📸 2 photos collected"
- **Thumbnails**: Preview all captured photos
- **Remove**: Click ×  on thumbnail to delete
- **Start Over**: Clear all and restart

### Buttons

- ➕ **Add Another Photo** - Capture next section
- ✅ **Process Receipt (3 photos)** - Submit all
- 🔄 **Start Over** - Clear and restart

---

## 🔧 Technical Details

### Frontend

- Multiple base64 images collected
- Sent as array to backend
- Thumbnail previews with remove option

### Backend

- Accepts `List[UploadFile]`
- Sends all images to Gemini in one call
- Gemini merges items automatically
- Returns single receipt with all items

### Gemini Prompt

```
You are analyzing MULTIPLE images of the SAME receipt.
- Combine ALL items from all images
- Use store/date/total from image that has it
- Merge items lists
- Remove duplicate items
```

---

## 📊 Example: 100-Item Aldi Receipt

**Workflow:**

1. **Photo 1**: Store name + items 1-35
2. **Photo 2**: Items 36-70
3. **Photo 3**: Items 71-100 + total

**Result:**
- Single receipt entry
- All 100 items with categories
- Correct total
- One database record

---

## ⚠️ Limitations

### Current:
- Up to ~5 photos per receipt (reasonable limit)
- Each image processed by Gemini
- Slight increase in processing time

### Best Practices:
- **2-3 photos** usually sufficient
- **Overlap** sections slightly for better merging
- **Good lighting** for all photos
- **Keep receipt flat** (no wrinkles)

---

## 🧪 Testing

### Test Scenario 1: Normal Receipt
- Upload single image
- Should work exactly as before

### Test Scenario 2: Long Receipt (2 photos)
- Capture top half
- Click "Add Another Photo"
- Capture bottom half
- Click "Process Receipt (2 photos)"
- Check all items present

### Test Scenario 3: Very Long Receipt (3+ photos)
- Capture in 3-4 sections
- Verify all items merged
- Check for duplicates (shouldn't have any)

---

## 🚀 What's Next?

This feature is now live at:
**https://app-receiptscan.netlify.app/**

Try it with your next long receipt!

---

## 📝 User Feedback

**Expected benefits:**
- ✅ No more missed items
- ✅ 100+ item receipts work perfectly
- ✅ Same database entry (no fragments)
- ✅ All items categorized properly

**Please report:**
- Duplicate items (shouldn't happen)
- Missing sections
- Merge errors
- Processing failures
