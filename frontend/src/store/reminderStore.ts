import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface DummyReminder {
  id: string;
  brokerId: number;
  policyNumber: string;
  customerName: string;
  premiumAmount: string;
  daysOverdue: number;
  sentAt: string;
}

interface ReminderState {
  reminders: DummyReminder[];
  addReminders: (reminders: DummyReminder[]) => void;
  clearReminders: () => void;
  getRemindersForBroker: (brokerId: number) => DummyReminder[];
}

const useReminderStore = create<ReminderState>()(
  persist(
    (set, get) => ({
      reminders: [],
      addReminders: (reminders) => set((state) => ({ reminders: [...state.reminders, ...reminders] })),
      clearReminders: () => set({ reminders: [] }),
      getRemindersForBroker: (brokerId) => get().reminders.filter(r => r.brokerId === brokerId),
    }),
    {
      name: 'reminder-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

export default useReminderStore; 