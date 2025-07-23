'use client';

import React from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import PolicyCreationForm from '@/components/PolicyCreationForm';

const CreatePolicyPage = () => {
  return (
    <Layout title="Create New Policy">
      <PolicyCreationForm />
    </Layout>
  );
};

export default withAuth(CreatePolicyPage); 