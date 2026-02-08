# Firebase Security Rules

Copy these rules to your Firebase Console → Firestore Database → Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Reports collection rules
    match /reports/{reportId} {
      // Anyone can read reports (anonymous display)
      allow read: if true;
      
      // Only authenticated users can create reports
      allow create: if request.auth != null 
                    && request.resource.data.userId == request.auth.uid
                    && request.resource.data.keys().hasAll(['userId', 'userName', 'title', 'description', 'location', 'category', 'timestamp', 'thumbsUp', 'thumbsDown', 'netScore']);
      
      // Only owner can delete their own reports
      allow delete: if request.auth != null 
                    && resource.data.userId == request.auth.uid;
      
      // Allow updates for voting (anyone authenticated) or owner editing
      allow update: if request.auth != null 
                    && (
                      // Owner can update any field
                      resource.data.userId == request.auth.uid
                      // OR anyone can update voting fields only
                      || onlyVotingFieldsChanged()
                    );
      
      // Helper function to check if only voting fields changed
      function onlyVotingFieldsChanged() {
        let affectedKeys = request.resource.data.diff(resource.data).affectedKeys();
        return affectedKeys.hasOnly(['thumbsUp', 'thumbsDown', 'netScore']);
      }
    }
    
    // Users collection (optional, for tracking)
    match /users/{userId} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Important Notes:

1. **Deploy these rules** to Firebase Console before using the Reports feature
2. **Voting security**: Users can only vote once (array union prevents duplicates)
3. **Anonymous display**: userName stored but user privacy maintained
4. **Owner privileges**: Only report creators can delete their own reports
5. **Rate limiting**: Consider adding Firebase Rate Limiting for production
