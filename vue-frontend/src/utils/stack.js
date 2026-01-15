export class Stack {
  constructor({ initialCapacity = 16, maxSize = Infinity } = {}) {
    if (!Number.isInteger(initialCapacity) || initialCapacity <= 0) {
      throw new Error("Stack: initialCapacity must be a positive integer")
    }
    if (!Number.isFinite(maxSize) || maxSize <= 0) {
      throw new Error("Stack: maxSize must be a positive number")
    }

    this._cap = initialCapacity
    this._arr = new Array(this._cap)
    this._top = 0
    this._max = maxSize
  }

  size() {
    return this._top
  }

  isEmpty() {
    return this._top === 0
  }

  maxSize() {
    return this._max
  }

  peek() {
    return this._top === 0 ? null : this._arr[this._top - 1]
  }

  push(item) {
    if (this._top >= this._max) {
      this._shiftLeftByOne()
      this._top -= 1
    }

    if (this._top >= this._cap) this._grow()
    this._arr[this._top] = item
    this._top += 1
    return this._top
  }

  pop() {
    if (this._top === 0) return null
    this._top -= 1
    const v = this._arr[this._top]
    this._arr[this._top] = undefined
    return v
  }

  clear() {
    for (let i = 0; i < this._top; i++) this._arr[i] = undefined
    this._top = 0
  }

  moveTopTo(otherStack) {
    if (!(otherStack instanceof Stack)) {
      throw new Error("Stack: moveTopTo expects another Stack")
    }
    const item = this.pop()
    if (item === null) return null
    otherStack.push(item)
    return item
  }

  toArray() {
    return this._arr.slice(0, this._top)
  }

  snapshot({ limit = 20 } = {}) {
    const n = Math.min(this._top, limit)
    return this._arr.slice(this._top - n, this._top)
  }

  _grow() {
    let newCap = this._cap * 2
    if (Number.isFinite(this._max)) newCap = Math.min(newCap, Math.max(this._cap + 1, this._max))
    const next = new Array(newCap)
    for (let i = 0; i < this._top; i++) next[i] = this._arr[i]
    this._arr = next
    this._cap = newCap
  }

  _shiftLeftByOne() {
    for (let i = 1; i < this._top; i++) this._arr[i - 1] = this._arr[i]
    this._arr[this._top - 1] = undefined
  }
}

export function createUndoRedo({ historyLimit = 200 } = {}) {
  const undo = new Stack({ initialCapacity: 32, maxSize: historyLimit })
  const redo = new Stack({ initialCapacity: 32, maxSize: historyLimit })

  function record(action) {
    undo.push(action)
    redo.clear()
  }

  return { undo, redo, record }
}
