# New Features: Sorting and Tag Management

This document outlines the new sorting and tag management features added to hwinfo-db.

## 🏷️ Tag System

### What it does
- Organize your PCs with custom colored tags (e.g., "Gaming", "Office", "Server")
- Each tag has a name and customizable color
- Multiple tags can be assigned to each PC

### How to use
1. Click "Manage Tags" in the header to create new tags
2. Choose a name and color for each tag
3. Tags will appear in the PC cards and can be used for filtering

### API Endpoints
- `GET /tags` - Get all tags
- `POST /tags` - Create a new tag
- `DELETE /tags/{id}` - Delete a tag
- `GET /pc/{id}/tags` - Get tags for a PC
- `POST /pc/{id}/tags` - Add tag to PC
- `DELETE /pc/{id}/tags/{tag_id}` - Remove tag from PC

## 📊 Sorting

### What it does
Sort your PC list by different criteria to find what you need quickly.

### Available sort options
- **Date Added** (default): Newest or oldest first
- **Hostname**: Alphabetical order
- **CPU**: Alphabetical order by CPU model

### How to use
1. Use the "Sort by" dropdown to select sorting criteria
2. Click the sort order button to toggle between ascending/descending
3. Results update automatically

### API Parameters
The `/pcs` endpoint now accepts query parameters:
- `sort_by`: `submitted_at`, `host`, or `cpu`
- `sort_order`: `asc` or `desc`

## 🔍 Filtering

### What it does
Filter your PC list to show only PCs with specific tags.

### How to use
1. Use the "Filter by tag" dropdown to select a tag
2. Only PCs with that tag will be displayed
3. Click "Clear Filter" to show all PCs again

### API Parameters
The `/pcs` endpoint accepts a `tag` parameter to filter by tag name.

## 🗃️ Database Changes

### New Tables
- **tag**: Stores tag definitions (id, name, color)
- **pc_tag**: Links PCs to tags (many-to-many relationship)

### Migration
For existing installations, run the migration script:
```bash
cd backend
python migrate_tags.py
```

This safely adds the new tables without affecting existing data.

## 🎨 UI Components

### New Components
- **FilterSortControls**: Header controls for sorting and filtering
- **TagManager**: Modal for creating and managing tags
- **Tag Badges**: Visual tag indicators on PC cards

### Enhanced Components
- **Card**: Now displays tags as colored badges
- **Main**: Supports sorting and filtering parameters
- **Home**: Integrates all new functionality

## 🔧 Technical Implementation

### Backend (Python/Flask)
- Enhanced `/pcs` endpoint with sorting and filtering
- New tag management endpoints
- Database schema updated with tag tables
- Migration script for existing installations

### Frontend (React/TypeScript)
- New TypeScript types for tags
- Enhanced API hooks with query parameters
- Reactive filtering and sorting
- Tag management UI with form validation

### Features
- Server-side sorting and filtering for performance
- Real-time updates when tags are modified
- Proper error handling and loading states
- Accessible UI components with Mantine

## 🚀 Benefits

1. **Better Organization**: Tags help categorize PCs by purpose or location
2. **Faster Navigation**: Sorting and filtering help find specific PCs quickly
3. **Visual Clarity**: Colored tags provide instant visual categorization
4. **Scalability**: Works efficiently even with many PCs in the database
5. **User Experience**: Intuitive controls that update results in real-time

## 📝 Usage Examples

### Creating Tags
```typescript
// Create a gaming PC tag
POST /tags
{
  "name": "Gaming",
  "color": "#228BE6"
}
```

### Filtering PCs
```
GET /pcs?tag=Gaming&sort_by=host&sort_order=asc
```

### Assigning Tags
```typescript
// Add "Gaming" tag to a PC
POST /pc/{pc_id}/tags
{
  "tag_id": 1
}
```

This enhancement makes hwinfo-db more scalable and user-friendly for managing multiple PCs across different categories and use cases.
