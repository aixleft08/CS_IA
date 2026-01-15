const TOMBSTONE = Symbol("TOMBSTONE")

function normalizeKey(key) {
  const t = typeof key
  if (t === "string") return key
  if (t === "number" || t === "boolean") return String(key)
  if (key == null) throw new Error("HashTable: key cannot be null/undefined")
  try {
    return JSON.stringify(key)
  } catch {
    throw new Error("HashTable: key must be serializable")
  }
}

export class HashTable {
  constructor(capacity = 257) {
    if (!Number.isInteger(capacity) || capacity <= 0) {
      throw new Error("HashTable: capacity must be a positive integer")
    }
    this._cap = capacity
    this._arr = new Array(capacity).fill(null)
    this._size = 0
  }

  size() {
    return this._size
  }

  isEmpty() {
    return this._size === 0
  }

  isFull() {
    return this._size >= this._cap
  }

  // djb2 hash function used
  // http://www.cse.yorku.ca/~oz/hash.html
  hashFunction(key) {
    const k = normalizeKey(key)
    let h = 5381
    for (let i = 0; i < k.length; i++) {
      h = ((h << 5) + h) ^ k.charCodeAt(i)
    }
    h = h >>> 0
    return h % this._cap
  }

  hasKey(key) {
    return this._findIndex(key) !== -1
  }

  isDuplicate(key) {
    return this.hasKey(key)
  }

  get(key) {
    const idx = this._findIndex(key)
    if (idx === -1) {
      throw new Error("HashTable: key does not exist")
    }
    return this._arr[idx].value
  }

  insertKey(key, value) {
    if (this.isFull()) {
      throw new Error("HashTable: table is full")
    }

    const k = normalizeKey(key)

    const existing = this._findIndex(k)
    if (existing !== -1) {
      throw new Error("HashTable: duplicate key")
    }

    const insertIdx = this._findInsertIndex(k)
    if (insertIdx === -1) {
      throw new Error("HashTable: no free slot found (full)")
    }

    this._arr[insertIdx] = { key: k, value }
    this._size += 1
    return true
  }

  removeKey(key) {
    const idx = this._findIndex(key)
    if (idx === -1) {
      throw new Error("HashTable: key does not exist")
    }
    this._arr[idx] = TOMBSTONE
    this._size -= 1
    return true
  }

  set(key, value) {
    const k = normalizeKey(key)
    const idx = this._findIndex(k)
    if (idx !== -1) {
      this._arr[idx].value = value
      return true
    }
    return this.insertKey(k, value)
  }

  keys() {
    const out = []
    for (const slot of this._arr) {
      if (slot && slot !== TOMBSTONE) out.push(slot.key)
    }
    return out
  }

  _findIndex(key) {
    const k = normalizeKey(key)
    let start = this.hashFunction(k)

    for (let step = 0; step < this._cap; step++) {
      const idx = (start + step) % this._cap
      const slot = this._arr[idx]

      if (slot === null) {
        return -1
      }
      if (slot === TOMBSTONE) continue
      if (slot.key === k) return idx
    }
    return -1
  }

  _findInsertIndex(key) {
    const k = normalizeKey(key)
    let start = this.hashFunction(k)
    let firstTombstone = -1

    for (let step = 0; step < this._cap; step++) {
      const idx = (start + step) % this._cap
      const slot = this._arr[idx]

      if (slot === null) {
        return firstTombstone !== -1 ? firstTombstone : idx
      }
      if (slot === TOMBSTONE) {
        if (firstTombstone === -1) firstTombstone = idx
        continue
      }
    }

    return firstTombstone !== -1 ? firstTombstone : -1
  }
}

export class HashSet {
  constructor(capacity = 257) {
    this._ht = new HashTable(capacity)
  }
  size() { return this._ht.size() }
  isEmpty() { return this._ht.isEmpty() }
  isFull() { return this._ht.isFull() }
  has(key) { return this._ht.hasKey(key) }
  add(key) {
    if (this.has(key)) return false
    return this._ht.insertKey(key, true)
  }
  remove(key) { return this._ht.removeKey(key) }
}
