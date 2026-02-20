import { describe, it, expect } from 'vitest'
import { cn } from './utils'

describe('utils', () => {
  describe('cn', () => {
    it('合并多个类名', () => {
      expect(cn('a', 'b', 'c')).toBe('a b c')
    })

    it('处理条件类名', () => {
      expect(cn('a', true && 'b', false && 'c')).toBe('a b')
    })

    it('处理空输入', () => {
      expect(cn()).toBe('')
    })

    it('处理 null 和 undefined', () => {
      expect(cn(null, undefined, 'a')).toBe('a')
    })

    it('处理 Tailwind 合并', () => {
      // px-2 和 px-4 冲突，后面的覆盖前面的
      expect(cn('px-2 text-red', 'px-4')).toBe('px-4 text-red')
    })

    it('处理重复类名', () => {
      expect(cn('a b', 'b c')).toBe('a b c')
    })
  })
})
