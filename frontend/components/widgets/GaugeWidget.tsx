'use client'

import { WidgetConfiguration } from '@/types/dashboard'
import { useEffect, useRef } from 'react'

interface GaugeWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function GaugeWidget({ widget, isEditing = false }: GaugeWidgetProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { title, data, config } = widget
  const value = data?.value || 0
  const min = data?.min || 0
  const max = data?.max || 100
  const label = data?.label || title || 'Score'
  const unit = data?.unit || ''
  const thresholds = config?.thresholds || [
    { value: 33, color: '#ef4444' },
    { value: 66, color: '#f59e0b' },
    { value: 100, color: '#10b981' }
  ]

  useEffect(() => {
    if (canvasRef.current) {
      drawGauge(canvasRef.current, value, min, max, thresholds)
    }
  }, [value, min, max])

  const drawGauge = (
    canvas: HTMLCanvasElement,
    currentValue: number,
    minValue: number,
    maxValue: number,
    colorThresholds: any[]
  ) => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height * 0.7
    const radius = Math.min(width, height) * 0.35

    ctx.clearRect(0, 0, width, height)

    const startAngle = Math.PI * 0.7
    const endAngle = Math.PI * 2.3
    const totalAngle = endAngle - startAngle

    ctx.lineWidth = radius * 0.15
    ctx.lineCap = 'round'

    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, startAngle, endAngle)
    ctx.strokeStyle = '#e5e7eb'
    ctx.stroke()

    const percentage = (currentValue - minValue) / (maxValue - minValue)
    const valueAngle = startAngle + (totalAngle * percentage)

    let gaugeColor = colorThresholds[0].color
    for (const threshold of colorThresholds) {
      if (percentage * 100 <= threshold.value) {
        gaugeColor = threshold.color
        break
      }
    }

    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, startAngle, valueAngle)
    ctx.strokeStyle = gaugeColor
    ctx.stroke()

    const pointerAngle = valueAngle
    const pointerLength = radius * 0.7
    const pointerX = centerX + Math.cos(pointerAngle) * pointerLength
    const pointerY = centerY + Math.sin(pointerAngle) * pointerLength

    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.lineTo(pointerX, pointerY)
    ctx.strokeStyle = '#1f2937'
    ctx.lineWidth = 3
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(centerX, centerY, radius * 0.08, 0, Math.PI * 2)
    ctx.fillStyle = '#1f2937'
    ctx.fill()

    ctx.font = 'bold 24px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillStyle = '#1f2937'
    ctx.fillText(
      `${Math.round(currentValue)}${unit}`,
      centerX,
      centerY + radius * 0.5
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 h-full flex flex-col ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      {label && (
        <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">{label}</h3>
      )}
      <div className="flex-1 flex items-center justify-center">
        <canvas
          ref={canvasRef}
          width={250}
          height={200}
          className="max-w-full h-auto"
        />
      </div>
      {data?.description && (
        <p className="text-sm text-gray-600 text-center mt-2">{data.description}</p>
      )}
    </div>
  )
}