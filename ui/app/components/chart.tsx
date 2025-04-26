"use client";
import {
  CategoryScale,
  ChartData,
  Chart as ChartJS,
  ChartOptions,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { CSSProperties } from "react";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
);

interface Breakdown {
  curve: Array<number>;
  data: Array<Array<number>>;
}

export default function ResultsChart({
  breakdown,
  className,
  style,
}: {
  breakdown: Breakdown;
  className?: string;
  style?: CSSProperties;
}) {
  const chart_opts: ChartOptions<"line"> = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Chart.js Line Chart",
      },
    },
  };

  const chart_data: ChartData<"line"> = {
    labels: breakdown.curve.map((_, idx) => idx),
    datasets: [
      {
        label: "model",
        data: breakdown.curve
          .map((value, idx) => {
            return { x: idx, y: value };
          })
          .filter((_, idx) => idx % 100 == 0),
        borderColor: "rgb(53, 162, 235)",
        backgroundColor: "rgba(53, 162, 235, 0.5)",
      },
      {
        label: "results",
        data: breakdown.data.map((value) => {
          return { x: value[0], y: value[1] };
        }),
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.5)",
        showLine: false,
      },
    ],
  };

  return (
    <Line
      options={chart_opts}
      data={chart_data}
      className={className}
      style={style}
    />
  );
}
