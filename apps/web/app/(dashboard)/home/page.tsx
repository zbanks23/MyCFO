import React from "react";

function page() {
  return (
    <section className="flex flex-col w-full h-full items-center">
      <div>Total Balance: $100,000</div>
      <div className="grid grid-cols-3 grid-rows-2 h-full w-full text-center">
        <div>Total Net Worth: $1,000,000</div>
        <div>Income vs Expenses line chart</div>
        <div>
          Spending Categories
          <ul>
            <li>Rent & Utilities: $1000</li>
            <li>Groceries: $300</li>
            <li>Transportation: $300</li>
            <li>Subscription: $50</li>
            <li>Dinning: $200</li>
            <li>Miscellaneous: $150</li>
          </ul>
        </div>
        <div>Income Sources bar chart</div>
        <div>Asset Pie Chart</div>
        <div>Savings Goal</div>
      </div>
    </section>
  );
}

export default page;
