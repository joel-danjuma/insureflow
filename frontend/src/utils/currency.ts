const USD_TO_NAIRA_RATE = 1500;

export const convertUSDToNaira = (usdAmount: number): string => {
  const nairaAmount = usdAmount * USD_TO_NAIRA_RATE;
  return `₦${nairaAmount.toLocaleString()}`;
};

export const formatNaira = (amount: number): string => {
  return `₦${amount.toLocaleString()}`;
};

export const parseCurrencyString = (currencyStr: string): number => {
  // Extract numeric value from currency strings like "$750,000" or "₦1,125,000"
  return parseFloat(currencyStr.replace(/[^\d.-]/g, ''));
}; 