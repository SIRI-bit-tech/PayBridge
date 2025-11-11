interface RealTimeIndicatorProps {
  isConnected: boolean
}

export function RealTimeIndicator({ isConnected }: RealTimeIndicatorProps) {
  return (
    <div
      className={`w-2 h-2 rounded-full ${
        isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
      }`}
      title={isConnected ? 'Connected' : 'Disconnected'}
    />
  )
}
