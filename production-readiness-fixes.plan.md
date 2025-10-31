<!-- c66a65a3-bf67-4723-9571-43e9de622cf8 5881e809-2454-4190-b2a6-4cd1e01a139d -->
# Fix Commissions Page Functionality and Responsiveness

This plan addresses critical issues with the commissions page that prevent brokers from viewing commission details, downloading receipts, and using the page effectively on mobile devices.

## Problem Analysis

The commissions page (`frontend/src/app/commissions/page.tsx`) has several critical issues:

1. **Non-functional buttons** - The "View", "Download", and "Request Payout" buttons have no onClick handlers, making them completely non-functional.

2. **Responsiveness issues** - The page has 10 columns in the table which causes horizontal scrolling on smaller screens. The table doesn't adapt to different screen sizes, forcing users to scroll horizontally to see all data.

3. **Data filtering bug** - Line 222 calls `.toLowerCase()` on `transaction_ref` without checking if it's defined, which could crash when filtering if some commissions have empty transaction references.

4. **Mock data** - The page uses hardcoded mock data instead of real API calls.

## Solution Approach

### 1. Add Button Functionality

- **Create CommissionDetailModal component** - A modal to display detailed commission information when "View" is clicked
- **Implement download functionality** - Generate/download invoice or receipt PDF when "Download" is clicked for paid commissions
- **Implement payout request** - Create a payout request modal/form when "Request Payout" is clicked
- **Wire up onClick handlers** - Connect all three buttons to their respective actions

### 2. Fix Responsiveness Issues

- **Add responsive column visibility** - Hide less critical columns on mobile/tablet screens using Tailwind responsive classes
- **Mobile-friendly column priority** - Show only essential columns (Policy Number, Client Name, Commission Amount, Status, Actions) on small screens
- **Hide secondary columns on mobile** - Commission Rate, Payment Method, Transaction Ref should be hidden on mobile
- **Make Actions column responsive** - Stack buttons vertically or use icon buttons on small screens
- **Add table wrapper improvements** - Ensure proper overflow handling with responsive container

### 3. Fix Data Filtering Bug

- **Add null/empty checks** - Validate `transaction_ref` exists and is not empty before calling `.toLowerCase()`
- **Provide safe filtering** - Handle undefined/null values gracefully in the filter function

### 4. Connect to Real API (Optional but Recommended)

- **Add commission service methods** - Create API service functions for fetching commissions
- **Replace mock data** - Connect to backend API endpoint for commission data
- **Handle loading/error states** - Add proper loading and error handling for API calls

## Implementation Steps

1. **Fix data filtering bug** - Add null checks before toLowerCase() calls
2. **Make table responsive** - Add Tailwind responsive classes to hide/show columns based on screen size
3. **Create commission detail modal** - Build modal component for viewing commission details
4. **Add download functionality** - Implement PDF generation or download for commission receipts
5. **Add payout request functionality** - Create payout request modal/form
6. **Wire up all button handlers** - Connect onClick handlers to new functionality
7. **Connect to real API** - Replace mock data with actual API calls (optional)

## Files to Create

- `frontend/src/components/CommissionDetailModal.tsx` - Modal for viewing commission details
- `frontend/src/components/PayoutRequestModal.tsx` - Modal for requesting payouts

## Files to Modify

- `frontend/src/app/commissions/page.tsx` - Add button handlers, fix responsiveness, fix data filtering
- `frontend/src/services/api.ts` - Add commission-related API service methods (if connecting to real API)

### To-dos

- [x] Update user CRUD functions to eagerly load the broker_profile relationship.
- [x] Add pagination support (skip/limit) to the backend endpoint for fetching client policies.
- [x] Implement a pagination UI on the frontend clients page and update data fetching logic.
- [x] Refactor the BrokerDashboard frontend component to include loading and error states.
- [x] Fix data filtering bug - Add null checks before toLowerCase() calls on transaction_ref
- [x] Make table responsive - Add Tailwind responsive classes to hide/show columns based on screen size
- [x] Create commission detail modal - Build modal component for viewing commission details
- [x] Add download functionality - Implement download for commission receipts (paid commissions)
- [x] Add payout request functionality - Create payout request modal/form with validation
- [x] Wire up all button handlers - Connect onClick handlers for View, Download, and Request Payout buttons
- [x] Update DataTable component - Add support for responsive column visibility via meta.className
- [ ] Connect to real API - Replace mock data with actual API calls (optional - not done)

