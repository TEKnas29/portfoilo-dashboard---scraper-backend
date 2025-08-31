// Mock data based on the images shown
const blogPosts = [
  {
    id: 1,
    date: 'Apr 18, 2024',
    title: 'CM Fixed Income: Exiting Banking & PSU to Add a New Gilt Fund',
    excerpt: 'We are increasing the duration of our Fixed Income portfolio to reflect the current macro conditions. We want to take advantage of the current higher rates to further increase the duration of the Gilt funds we hold.',
    category: 'Fixed Income'
  },
  {
    id: 2,
    date: 'Apr 05, 2024',
    title: 'Craftsman Automation: Poised for Growth Amid Temporary Headwinds',
    excerpt: 'Unlock this post by trial. Craftsman Automation excels in making precise parts for cars and machines. Amidst temporary headwinds, looks resilient with a focus on growth and innovation.',
    category: 'Equity Research'
  },
  {
    id: 3,
    date: 'Apr 03, 2024',
    title: 'The Focused Way of Investing: Our Four-Quadrant Strategy and FY24 Review',
    excerpt: 'FY24 brought us a 42% gain in our Capitalmind Focused portfolio, gently outperforming the Nifty\'s 29%. It\'s been a bit of a rollercoaster, especially these last few months, but that\'s part of the equity investing.',
    category: 'Strategy'
  },
  {
    id: 4,
    date: 'Mar 27, 2024',
    title: 'A Small CAD for India, Yet Again',
    excerpt: 'Yet again, India\'s Current Account Deficit is a mere 10 bp in the quarter (Dec 2023), less than levels more than a decade back, and less than 2017-18 too. Why net of gold? It\'s not really a current account import.',
    category: 'Economic Analysis'
  },
  {
    id: 5,
    date: 'Mar 25, 2024',
    title: 'Poonawalla Fincorp: One right step at a time',
    excerpt: 'There are some winning patterns in investing that keep repeating. One such pattern is when a big company buys a struggling company, fixes old problems, and brings in new leadership to grow the business.',
    category: 'Equity Research'
  },
  {
    id: 6,
    date: 'Mar 18, 2024',
    title: 'CM Focused: Reducing our allocation to smallcaps & increasing cash',
    excerpt: 'In the last few days, we have seen increased volatility in the mid and small-cap companies. Smallcaps especially have corrected, and while we did not see an immediate way ahead.',
    category: 'Portfolio Update'
  }
];

// Mock portfolio data based on the performance table shown
const portfolioReturns = {
  focused: {
    ytd: -1.7,
    '1d': 0.1,
    '1w': 2.9,
    '1m': 7.6,
    '3m': 2.2,
    '6m': 10.1,
    '1y': 43.5,
    '3y': 23.9,
    si: 22.5,
    dd: -2.8,
    maxdd: -40.3
  },
  nifty50: {
    ytd: 3.1,
    '1d': 0.1,
    '1w': 1.1,
    '1m': 1.4,
    '3m': 4.4,
    '6m': 16.2,
    '1y': 26.2,
    '3y': 16.0,
    si: 14.5,
    dd: -1.5,
    maxdd: -38.4
  }
};

// Mock equity curve data
const equityCurveData = [
  { date: '2019-01', focused: 100, nifty: 100, drawdown: 0 },
  { date: '2019-06', focused: 105, nifty: 103, drawdown: -2 },
  { date: '2020-01', focused: 110, nifty: 108, drawdown: -5 },
  { date: '2020-03', focused: 85, nifty: 78, drawdown: -20 },
  { date: '2020-06', focused: 95, nifty: 88, drawdown: -10 },
  { date: '2020-12', focused: 125, nifty: 115, drawdown: -5 },
  { date: '2021-06', focused: 145, nifty: 135, drawdown: -3 },
  { date: '2021-12', focused: 165, nifty: 155, drawdown: -2 },
  { date: '2022-06', focused: 155, nifty: 145, drawdown: -8 },
  { date: '2022-12', focused: 170, nifty: 160, drawdown: -5 },
  { date: '2023-06', focused: 195, nifty: 180, drawdown: -3 },
  { date: '2023-12', focused: 225, nifty: 200, drawdown: -2 },
  { date: '2024-03', focused: 285, nifty: 205, drawdown: -1 }
];

const monthlyReturns = [
  { month: 'Jan 24', focused: 2.1, nifty: 1.2 },
  { month: 'Feb 24', focused: 4.2, nifty: 2.8 },
  { month: 'Mar 24', focused: 1.8, nifty: 3.1 },
  { month: 'Apr 24', focused: -1.7, nifty: 0.9 }
];

export { blogPosts, portfolioReturns, equityCurveData, monthlyReturns };