import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Label } from '@/components/ui/label'
import { useTheme, type ThemeMode } from '@/contexts/ThemeContext'

interface ThemeSettingsProps {
  className?: string
}

const THEME_OPTIONS: { value: ThemeMode; label: string; description: string }[] = [
  { value: 'dark', label: 'Dark', description: '深蓝色调，适合夜间使用' },
  { value: 'gray', label: 'Gray', description: '中性灰色调，简洁舒适' },
  { value: 'light', label: 'Light', description: '浅色主题，适合白天使用' },
  { value: 'custom', label: 'Custom', description: '自定义颜色' },
]

const COLOR_KEYS: { key: keyof import('@/contexts/ThemeContext').CustomThemeColors; label: string }[] = [
  { key: 'background', label: 'Background' },
  { key: 'foreground', label: 'Foreground' },
  { key: 'card', label: 'Card' },
  { key: 'cardForeground', label: 'Card Foreground' },
  { key: 'primary', label: 'Primary' },
  { key: 'primaryForeground', label: 'Primary Foreground' },
  { key: 'secondary', label: 'Secondary' },
  { key: 'secondaryForeground', label: 'Secondary Foreground' },
  { key: 'muted', label: 'Muted' },
  { key: 'mutedForeground', label: 'Muted Foreground' },
  { key: 'accent', label: 'Accent' },
  { key: 'accentForeground', label: 'Accent Foreground' },
  { key: 'destructive', label: 'Destructive' },
  { key: 'destructiveForeground', label: 'Destructive Foreground' },
  { key: 'border', label: 'Border' },
  { key: 'input', label: 'Input' },
  { key: 'ring', label: 'Ring' },
]

export function ThemeSettings({ className }: ThemeSettingsProps) {
  const { theme, setTheme, customColors, setCustomColors } = useTheme()

  return (
    <div className={cn('space-y-6', className)}>
      {/* Theme Selector */}
      <div className="space-y-3">
        <div>
          <h3 className="text-sm font-medium">主题</h3>
          <p className="text-xs text-muted-foreground mt-1">选择你喜欢的颜色主题</p>
        </div>
        <div className="flex items-center gap-1 p-1 bg-muted/30 rounded-lg">
          {THEME_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setTheme(option.value)}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                theme === option.value
                  ? 'bg-background shadow-sm'
                  : 'hover:bg-background/50'
              )}
              title={option.description}
            >
              {theme === option.value && <Check className="h-3 w-3" />}
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Color Editor */}
      {theme === 'custom' && (
        <div className="space-y-4 p-4 border border-border rounded-lg bg-muted/20">
          <div>
            <h4 className="text-sm font-medium">自定义主题颜色</h4>
            <p className="text-xs text-muted-foreground mt-1">
              使用 CSS 颜色值 (hex, rgb, hsl 等)。更改会立即应用。
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {COLOR_KEYS.map(({ key, label }) => (
              <div key={key} className="space-y-2">
                <Label htmlFor={`color-${key}`} className="text-xs">
                  {label}
                </Label>
                <div className="flex gap-2">
                  <input
                    id={`color-${key}`}
                    type="text"
                    value={customColors[key]}
                    onChange={(e) => setCustomColors({ [key]: e.target.value })}
                    placeholder="hsl(240 10% 3.9%)"
                    className="flex-1 h-9 px-3 py-1 text-xs font-mono rounded-md border border-input bg-background shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  />
                  <div
                    className="w-9 h-9 rounded border border-border shrink-0"
                    style={{ backgroundColor: customColors[key] }}
                    title={customColors[key]}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Reset Button */}
          <div className="pt-2 border-t border-border">
            <button
              onClick={() => {
                // Reset to default dark theme colors
                const defaultColors = {
                  background: 'hsl(240 10% 3.9%)',
                  foreground: 'hsl(0 0% 98%)',
                  card: 'hsl(240 10% 3.9%)',
                  cardForeground: 'hsl(0 0% 98%)',
                  primary: 'hsl(0 0% 98%)',
                  primaryForeground: 'hsl(240 5.9% 10%)',
                  secondary: 'hsl(240 3.7% 15.9%)',
                  secondaryForeground: 'hsl(0 0% 98%)',
                  muted: 'hsl(240 3.7% 15.9%)',
                  mutedForeground: 'hsl(240 5% 64.9%)',
                  accent: 'hsl(240 3.7% 15.9%)',
                  accentForeground: 'hsl(0 0% 98%)',
                  destructive: 'hsl(0 62.8% 30.6%)',
                  destructiveForeground: 'hsl(0 0% 98%)',
                  border: 'hsl(240 3.7% 15.9%)',
                  input: 'hsl(240 3.7% 15.9%)',
                  ring: 'hsl(240 4.9% 83.9%)',
                }
                Object.entries(defaultColors).forEach(([key, value]) => {
                  setCustomColors({ [key as keyof typeof defaultColors]: value })
                })
              }}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              重置为默认颜色
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
