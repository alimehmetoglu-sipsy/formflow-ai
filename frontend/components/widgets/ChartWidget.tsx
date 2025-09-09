'use client'

import { WidgetConfiguration, ChartType } from '@/types/dashboard'
import { useEffect, useRef } from 'react'

interface ChartWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function ChartWidget({ widget, isEditing = false }: ChartWidgetProps) {
  const chartRef = useRef<HTMLCanvasElement>(null)
  const { title, description, config, data } = widget
  const chartType = config?.chartType || 'bar'

  useEffect(() => {
    if (chartRef.current && data) {
      renderChart(chartRef.current, chartType, data, config)
    }
  }, [data, chartType, config])

  const renderChart = (
    canvas: HTMLCanvasElement,
    type: ChartType,
    chartData: any,
    chartConfig: any
  ) => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    ctx.clearRect(0, 0, width, height)

    const colors = [
      '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
      '#06b6d4', '#f97316', '#ef4444', '#84cc16', '#a855f7'
    ]

    if (type === 'bar') {
      drawBarChart(ctx, width, height, chartData, colors)
    } else if (type === 'line') {
      drawLineChart(ctx, width, height, chartData, colors[0])
    } else if (type === 'pie' || type === 'donut') {
      drawPieChart(ctx, width, height, chartData, colors, type === 'donut')
    }
  }

  const drawBarChart = (
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    data: any,
    colors: string[]
  ) => {
    if (!data.labels || !data.values) return

    const padding = 40
    const barWidth = (width - padding * 2) / data.labels.length
    const maxValue = Math.max(...data.values)
    const scale = (height - padding * 2) / maxValue

    data.values.forEach((value: number, i: number) => {
      const barHeight = value * scale
      const x = padding + i * barWidth + barWidth * 0.1
      const y = height - padding - barHeight
      const w = barWidth * 0.8
      
      ctx.fillStyle = colors[i % colors.length]
      ctx.fillRect(x, y, w, barHeight)
      
      ctx.fillStyle = '#6b7280'
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(
        data.labels[i],
        x + w / 2,
        height - padding + 20
      )
    })
  }

  const drawLineChart = (
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    data: any,
    color: string
  ) => {
    if (!data.labels || !data.values) return

    const padding = 40
    const maxValue = Math.max(...data.values)
    const xStep = (width - padding * 2) / (data.values.length - 1)
    const yScale = (height - padding * 2) / maxValue

    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.beginPath()

    data.values.forEach((value: number, i: number) => {
      const x = padding + i * xStep
      const y = height - padding - value * yScale

      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }

      ctx.fillStyle = color
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, Math.PI * 2)
      ctx.fill()
    })

    ctx.stroke()
  }

  const drawPieChart = (
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    data: any,
    colors: string[],
    isDonut: boolean
  ) => {
    if (!data.labels || !data.values) return

    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) / 2 - 20
    const total = data.values.reduce((a: number, b: number) => a + b, 0)
    let currentAngle = -Math.PI / 2

    data.values.forEach((value: number, i: number) => {
      const sliceAngle = (value / total) * Math.PI * 2
      
      ctx.fillStyle = colors[i % colors.length]
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
      ctx.closePath()
      ctx.fill()

      currentAngle += sliceAngle
    })

    if (isDonut) {
      ctx.fillStyle = '#ffffff'
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius * 0.6, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 h-full ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      )}
      {description && (
        <p className="text-sm text-gray-600 mb-3">{description}</p>
      )}
      <div className="relative w-full h-full min-h-[200px]">
        <canvas
          ref={chartRef}
          width={400}
          height={300}
          className="w-full h-full"
        />
      </div>
    </div>
  )
}