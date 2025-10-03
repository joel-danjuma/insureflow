const USD_TO_NAIRA_RATE = 1500;

export const convertUSDToNaira = (usdAmount: number): string => {
  const nairaAmount = usdAmount * USD_TO_NAIRA_RATE;
  return formatNaira(nairaAmount);
};

export const formatNaira = (amount: number): string => {
  // Handle edge cases: NaN, undefined, null, or non-numeric values
  if (typeof amount !== 'number' || isNaN(amount) || amount === null || amount === undefined) {
    return '₦0';
  }
  
  const options: Intl.NumberFormatOptions = { 
    style: 'currency', 
    currency: 'NGN',
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  };
  
  if (Number.isInteger(amount)) {
    options.minimumFractionDigits = 0;
    options.maximumFractionDigits = 0;
  }
  
  try {
    const formatter = new Intl.NumberFormat('en-NG', options);
    return formatter.format(amount).replace('NGN', '₦');
  } catch (error) {
    // Fallback if formatting fails
    return `₦${amount.toLocaleString()}`;
  }
};

export const parseCurrencyString = (currencyStr: string): number => {
  // Extract numeric value from currency strings like "$750,000" or "₦1,125,000"
  return parseFloat(currencyStr.replace(/[^\d.-]/g, ''));
}; 