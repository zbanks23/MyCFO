"use client";

import React, { useState, useCallback } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
} from "@dnd-kit/core";

const WidgetDashboard: React.FC = () => {
  return (
    <div className="grid h-screen xl:w-full text-center gap-4 grid-cols-4 grid-rows-3 p-8">
      <div className="rounded-lg bg-gray-700 p-4">
        Total Net Worth: $1,000,000
      </div>
      <div className="col-span-2 rounded-lg bg-gray-700 p-4">
        Total Cash Balance: $100,000
      </div>
      <div className="row-span-2 rounded-lg bg-gray-700 p-4">
        Budget Bar Chart
        <ul>
          <li>Rent & Utilities: $1000</li>
          <li>Groceries: $300</li>
          <li>Transportation: $300</li>
          <li>Subscription: $50</li>
          <li>Dinning: $200</li>
          <li>Miscellaneous: $150</li>
        </ul>
      </div>
      <div className="col-span-2 row-span-2 rounded-lg bg-gray-700 p-4">
        Expenses Pie Chart
      </div>
      <div className="rounded-lg bg-gray-700 p-4">Income Sources bar chart</div>
      <div className="rounded-lg bg-gray-700 p-4">Stock Watchlist</div>
      <div className="rounded-lg bg-gray-700 p-4">Savings Goal</div>
    </div>
  );
};

export default WidgetDashboard;
