'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { supportService } from '@/services/api';

interface SupportTicket {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}

interface FAQ {
  id: number;
  question: string;
  answer: string;
  category: string;
}

const SupportPage = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'tickets' | 'faq'>('tickets');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [ticketForm, setTicketForm] = useState({
    title: '',
    description: '',
    priority: 'medium' as 'low' | 'medium' | 'high',
    category: 'general' as string,
  });

  // Fetch tickets from API
  const { data: tickets = [], isLoading: ticketsLoading, refetch } = useQuery({
    queryKey: ['support-tickets'],
    queryFn: async () => {
      try {
        const data = await supportService.getTickets();
        return data;
      } catch (error) {
        console.error('Error fetching tickets:', error);
        return [];
      }
    },
  });

  const { data: faqs = [] } = useQuery({
    queryKey: ['faqs'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return [
        {
          id: 1,
          question: 'How do I create a new policy?',
          answer: 'Navigate to the Create Policy page from the sidebar, fill in all required fields, and submit the form. You will receive a confirmation email once the policy is created.',
          category: 'Policies',
        },
        {
          id: 2,
          question: 'What payment methods are accepted?',
          answer: 'We accept bank transfers, card payments, and mobile money transfers. All payments are processed securely through our payment gateway.',
          category: 'Payments',
        },
        {
          id: 3,
          question: 'How are commissions calculated?',
          answer: 'Commissions are calculated as a percentage of the premium amount. The standard rate is 15% for brokers, but this may vary based on your agreement.',
          category: 'Commissions',
        },
        {
          id: 4,
          question: 'How long does payment processing take?',
          answer: 'Payment processing typically takes 1-3 business days. You will receive a confirmation email once the payment is processed.',
          category: 'Payments',
        },
        {
          id: 5,
          question: 'Can I edit a policy after creation?',
          answer: 'Yes, you can edit certain fields of a policy after creation. However, some fields like policy number and start date cannot be modified.',
          category: 'Policies',
        },
        {
          id: 6,
          question: 'How do I contact customer support?',
          answer: 'You can submit a support ticket through this page, email us at support@insureflow.com, or call us at +234 800 123 4567.',
          category: 'General',
        },
      ];
    },
  });

  const handleSubmitTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage(null);

    try {
      await supportService.createTicket({
        title: ticketForm.title,
        description: ticketForm.description,
        category: ticketForm.category,
        priority: ticketForm.priority,
      });
      
      setMessage({ type: 'success', text: 'Support ticket submitted successfully! We will get back to you within 24 hours.' });
      setTicketForm({
        title: '',
        description: '',
        priority: 'medium',
        category: 'general',
      });
      
      // Refetch tickets to show the new ticket
      queryClient.invalidateQueries({ queryKey: ['support-tickets'] });
      refetch();
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to submit ticket. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      open: 'bg-blue-900/30 text-blue-400 border-blue-500/30',
      in_progress: 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30',
      resolved: 'bg-green-900/30 text-green-400 border-green-500/30',
      closed: 'bg-gray-900/30 text-gray-400 border-gray-500/30',
    };
    return colors[status as keyof typeof colors] || colors.closed;
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      low: 'bg-green-900/30 text-green-400 border-green-500/30',
      medium: 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30',
      high: 'bg-red-900/30 text-red-400 border-red-500/30',
    };
    return colors[priority as keyof typeof colors] || colors.medium;
  };

  if (ticketsLoading) {
    return (
      <Layout title="Support">
        <div className="max-w-4xl mx-auto p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Support</h1>
            <p className="text-gray-400">Get help and submit support tickets</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-700 rounded w-1/4"></div>
              <div className="h-4 bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Support">
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Support</h1>
          <p className="text-gray-400">Get help and submit support tickets</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-900/20 border border-green-500/30 text-green-400' 
              : 'bg-red-900/20 border border-red-500/30 text-red-400'
          }`}>
            {message.text}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('tickets')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'tickets'
                ? 'bg-orange-500 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            My Tickets
          </button>
          <button
            onClick={() => setActiveTab('faq')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'faq'
                ? 'bg-orange-500 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            FAQ
          </button>
        </div>

        {activeTab === 'tickets' && (
          <div className="space-y-6">
            {/* Submit New Ticket */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Submit New Ticket</h3>
              <form onSubmit={handleSubmitTicket} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Ticket Title *
                    </label>
                    <input
                      type="text"
                      value={ticketForm.title}
                      onChange={(e) => setTicketForm(prev => ({ ...prev, title: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Priority *
                    </label>
                    <select
                      value={ticketForm.priority}
                      onChange={(e) => setTicketForm(prev => ({ ...prev, priority: e.target.value as 'low' | 'medium' | 'high' }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Category *
                    </label>
                    <select
                      value={ticketForm.category}
                      onChange={(e) => setTicketForm(prev => ({ ...prev, category: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
                    >
                      <option value="general">General</option>
                      <option value="policies">Policies</option>
                      <option value="payments">Payments</option>
                      <option value="commissions">Commissions</option>
                      <option value="technical">Technical</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Description *
                  </label>
                  <textarea
                    value={ticketForm.description}
                    onChange={(e) => setTicketForm(prev => ({ ...prev, description: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
                    placeholder="Please describe your issue in detail..."
                    required
                  />
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50 transition-colors"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Ticket'}
                  </button>
                </div>
              </form>
            </div>

            {/* Existing Tickets */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">My Support Tickets</h3>
              <div className="space-y-4">
                {tickets.map((ticket) => (
                  <div key={ticket.id} className="border border-gray-700 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="text-white font-medium">{ticket.title}</h4>
                        <p className="text-gray-400 text-sm mt-1">{ticket.description}</p>
                      </div>
                      <div className="flex space-x-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(ticket.status)}`}>
                          {ticket.status.replace('_', ' ').charAt(0).toUpperCase() + ticket.status.replace('_', ' ').slice(1)}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getPriorityColor(ticket.priority)}`}>
                          {ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}
                        </span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-sm text-gray-400">
                      <span>Created: {new Date(ticket.created_at).toLocaleDateString()}</span>
                      <span>Updated: {new Date(ticket.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
                {tickets.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-gray-400">No support tickets found.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'faq' && (
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Frequently Asked Questions</h3>
            <div className="space-y-6">
              {faqs.map((faq) => (
                <div key={faq.id} className="border border-gray-700 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-2">{faq.question}</h4>
                  <p className="text-gray-400">{faq.answer}</p>
                  <div className="mt-3">
                    <span className="inline-block px-2 py-1 bg-orange-500/20 text-orange-400 text-xs rounded">
                      {faq.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default withAuth(SupportPage); 