import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { Download, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { NAVData } from "../navdata";

interface NavDataItem {
  date: string;
  NAV: string;
  nifty?: number;
  drawdown?: number;
}

const PortfolioPage = () => {
  const [fromDate, setFromDate] = useState("2019-01-01");
  const [toDate, setToDate] = useState("2024-04-24");
  const [filteredData, setFilteredData] = useState<NavDataItem[]>(NAVData);

  useEffect(() => {
    // Add the new fields to NAVData
    const dataWithExtraFields = NAVData.map((item) => {
      const percent = Math.random() * 6 - 3;
      const delta = (Number(item.NAV) * percent) / 100;
      return {
        ...item,
        nifty: +(Number(item.NAV) + delta).toFixed(2),
        drawdown: +delta.toFixed(2),
      };
    });

    const result = dataWithExtraFields
      .filter((item) => {
        const d = new Date(item.date);
        return (
          (!fromDate || d >= new Date(fromDate)) &&
          (!toDate || d <= new Date(toDate))
        );
      })
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()); // sort ascending by date

    setFilteredData(result);
  }, [fromDate, toDate]);

  function handleReset(): void {
    setFromDate("2019-01-01");
    setToDate("2024-04-24");
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-white">
      {/* Trailing Returns Table */}
      <div className="mb-8">
        <div className="p-6 border-b flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            Trailing Returns
          </h2>
          <button className="text-teal-600 hover:text-teal-700">
            <Download size={20} />
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {[
                  "Name",
                  "YTD",
                  "1D",
                  "1W",
                  "1M",
                  "3M",
                  "6M",
                  "1Y",
                  "3Y",
                  "SI",
                  "DD",
                  "MAXDD",
                ].map((head) => (
                  <th
                    key={head}
                    className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${
                      head === "SI" ? "border-r border-gray-300" : ""
                    }`}
                  >
                    {head}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <TableRow
                name="Focused"
                data={[
                  "-1.7%",
                  "0.1%",
                  "2.9%",
                  "7.6%",
                  "2.2%",
                  "10.1%",
                  "43.5%",
                  "23.9%",
                  "22.5%",
                  "-2.8%",
                  "-40.3%",
                ]}
              />
              <TableRow
                name="NIFTY50"
                data={[
                  "3.1%",
                  "0.1%",
                  "1.1%",
                  "1.4%",
                  "4.4%",
                  "16.2%",
                  "26.2%",
                  "16.0%",
                  "14.5%",
                  "-1.5%",
                  "-38.4%",
                ]}
              />
            </tbody>
          </table>
        </div>

        <div className="px-6 py-3">
          <p className="text-xs text-gray-500">
            Note: Returns above 1 year are annualised
          </p>
        </div>
      </div>

      {/* Equity Curve */}
      <div className="bg-white">
        <div className="p-6">
          <div className="flex justify-between items-start">
            {/* Left side - Title and info */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Equity curve
              </h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Live since 2019-01-01
                </span>
                <button
                  onClick={handleReset}
                  className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs hover:bg-green-200 transition-colors"
                >
                  <RotateCcw size={16} className="mr-1 inline-block" />
                  Reset
                </button>
              </div>
            </div>

            {/* Right side - Date inputs */}
            <div className="flex items-end space-x-4">
              <DateInput
                label="From date"
                value={fromDate}
                onChange={setFromDate}
              />
              <DateInput label="To date" value={toDate} onChange={setToDate} />
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="h-[400px]">
            <ResponsiveContainer>
              <LineChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="NAV"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="NAV"
                />
                <Line
                  type="monotone"
                  dataKey="nifty"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="NIFTY50"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Drawdown (Area chart) */}
          <div className="h-[150px] mt-6">
            <ResponsiveContainer>
              <AreaChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="drawdown"
                  stroke="#ef4444"
                  fill="#ef4444"
                  fillOpacity={0.3}
                  name="Drawdown"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

interface TableRowProps {
  name: string;
  data: string[];
}

const TableRow = ({ name, data }: TableRowProps) => (
  <tr>
    <td className="px-6 py-4 text-sm font-medium text-gray-900">{name}</td>
    {data.map((val: string, i: number) => (
      <td
        key={i}
        className={`px-6 py-4 text-sm ${
          val.startsWith("-") ? "text-red-600" : "text-green-600"
        } ${i === 8 ? "border-r border-gray-300" : ""}`}
      >
        {val}
      </td>
    ))}
  </tr>
);

interface DateInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

const DateInput = ({ label, value, onChange }: DateInputProps) => (
  <div className="flex flex-col">
    <label className="text-xs text-gray-600 mb-1">{label}</label>
    <input
      type="date"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="appearance-none block w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-teal-500 focus:border-teal-500"
    />
  </div>
);

export default PortfolioPage;
