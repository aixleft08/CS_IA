<script setup>
import { ref } from 'vue'

const props = defineProps({
  rows:         { type: Array,   required: true },
  loading:      { type: Boolean, default: false },
  error:        { type: String,  default: '' },
  last:         { type: Object,  default: null },
  lastLoading:  { type: Boolean, default: false },
  lastError:    { type: String,  default: '' },
})
const emit = defineEmits(['reset', 'add', 'delete', 'toggle-details'])

const newWord = ref('')
const expandedId = ref(null)

function submitAdd() {
  const w = newWord.value.trim()
  if (!w) return
  emit('add', w)
  newWord.value = ''
}

function toggleRow(row) {
  emit('toggle-details', row)
  expandedId.value = expandedId.value === row.id ? null : row.id
}
</script>

<template>
  <section class="wrap">
    <h1 class="title">
      Wordbank
      <span v-if="rows.length" class="count">({{ rows.length }})</span>
    </h1>

    <p class="sub">
      <template v-if="lastLoading">
        figuring out where you left off…
      </template>

      <template v-else-if="last && last.id">
        You were reading
        <router-link :to="`/read/${last.id}`" class="inline-link">
          {{ last.title }}
        </router-link>.
      </template>

      <template v-else-if="lastError">
        <span style="color:#a33">Couldn’t fetch last reading.</span>
      </template>

      <template v-else>
        Start by picking an article in
        <router-link to="/search" class="inline-link">Search</router-link>.
      </template>
    </p>

    <form class="add-row" @submit.prevent="submitAdd">
      <input
        v-model="newWord"
        placeholder="Add a new word…"
        :disabled="loading"
      />
      <button type="submit" :disabled="loading">
        Add
      </button>
    </form>

    <div class="table">
      <div class="thead">
        <div>#</div>
        <div>Word</div>
        <div></div>
      </div>

      <div v-if="loading" class="trow">
        <div></div>
        <div class="bold">Loading…</div>
        <div></div>
      </div>

      <div v-else-if="error" class="trow">
        <div></div>
        <div class="bold" style="color:#c33">{{ error }}</div>
        <div></div>
      </div>

      <div v-else-if="!rows.length" class="trow">
        <div></div>
        <div class="bold">No words yet.</div>
        <div></div>
      </div>

      <div
        v-else
        v-for="(r, i) in rows"
        :key="r.id"
        class="row-group"
      >
        <div class="trow clickable" @click="toggleRow(r)">
          <div>{{ i + 1 }}</div>
          <div class="bold">
            {{ r.word }}
            <span v-if="r.translation" class="translation">
              {{ r.translation }}
            </span>
          </div>
          <div class="actions-cell">
            <button
              class="link-btn"
              type="button"
              @click.stop="$emit('delete', r.id)"
              aria-label="Delete word"
            >
              Delete
            </button>
          </div>
        </div>

        <div v-if="expandedId === r.id" class="expand">
          <p v-if="r.entryError" class="expand-error">
            {{ r.entryError }}
          </p>

          <div v-else-if="r.entry && r.entry.length">
            <div
              v-for="(entry, ei) in r.entry"
              :key="ei"
              class="entry-block"
            >
              <p v-if="entry.phonetic" class="phonetic">
                /{{ entry.phonetic }}/
              </p>

              <div
                v-for="(m, mi) in entry.meanings"
                :key="mi"
                class="meaning"
              >
                <p class="pos">{{ m.partOfSpeech }}</p>

                <template v-if="m.definitions && m.definitions.length">
                  <p class="def-line">
                    {{ m.definitions[0].definition }}
                  </p>
                  <p
                    v-if="m.definitions[0].example"
                    class="example"
                  >
                    “{{ m.definitions[0].example }}”
                  </p>
                </template>

                <p v-else class="def-line muted">
                  No definition found
                </p>
              </div>
            </div>
          </div>

          <p v-else class="expand-loading">
            Loading definition…
          </p>
        </div>
      </div>
    </div>

    <div class="actions">
      <button
        class="ghost"
        type="button"
        @click="$emit('reset')"
        :disabled="loading || !rows.length"
      >
        Reset wordbank
      </button>
    </div>
  </section>
</template>

<style scoped>
.wrap{
  background:#fff;
  border-radius:12px;
  box-shadow:0 10px 25px rgba(0,0,0,.1);
  padding:2rem 2.25rem;
  max-width:1000px;
  margin:0 auto;
}
.title{
  margin:0 0 .25rem;
  text-align:center;
  font-size:2rem;
}
.count{
  font-size:.95rem;
  font-weight:500;
  color:#777;
  margin-left:.4rem;
}
.sub{
  margin:0 0 1.25rem;
  text-align:center;
  color:#666;
}
.inline-link{
  color:#667eea;
  text-decoration:underline;
}
.add-row{
  display:flex;
  gap:.5rem;
  margin-bottom:1rem;
}
.add-row input{
  flex:1;
  padding:.5rem .75rem;
  border:1px solid #d1d5db;
  border-radius:6px;
}
.add-row input:disabled{
  background:#f3f4f6;
}
.add-row button{
  background:#333;
  color:#fff;
  border:none;
  border-radius:6px;
  padding:.5rem .9rem;
  cursor:pointer;
}
.add-row button:disabled{
  opacity:.6;
  cursor:not-allowed;
}

.table{
  border:2px solid #cfd4dc;
  border-radius:8px;
  overflow:hidden;
}
.thead{
  display:grid;
  grid-template-columns:80px 1fr 120px;
  background:#f3f4f6;
  font-weight:800;
}
.thead>div{
  padding:.9rem 1rem;
  border-bottom:2px solid #e5e7eb;
}
.row-group{
  border-bottom:1px solid #e5e7eb;
}
.trow{
  display:grid;
  grid-template-columns:80px 1fr 120px;
  align-items:center;
  padding:.9rem 1rem;
  gap:1rem;
}
.clickable{
  cursor:pointer;
}
.actions-cell{
  text-align:right;
}
.link-btn{
  background:none;
  border:none;
  color:#c33;
  cursor:pointer;
  font-weight:600;
}

.translation{
  display:block;
  color:#7b7b7b;
  font-size:.85rem;
  margin-top:.1rem;
}

.expand{
  background:#f9fafb;
  padding:.9rem 1rem 1.2rem;
}
.expand-loading{
  color:#888;
  font-size:.875rem;
}
.expand-error{
  color:#c33;
  font-size:.875rem;
}
.entry-block{
  margin-bottom:1rem;
}
.phonetic{
  font-style:italic;
  color:#555;
  margin-bottom:.5rem;
}
.meaning{
  margin-bottom:.75rem;
}
.pos{
  font-weight:600;
  text-transform:capitalize;
  margin-bottom:.25rem;
}
.def-line{
  margin-bottom:.25rem;
}
.muted{
  color:#666;
}
.example{
  color:#555;
  font-size:.8rem;
  margin-top:.15rem;
}
.actions{
  display:flex;
  justify-content:flex-end;
  margin-top:1.25rem;
}
.ghost{
  padding:.7rem 1rem;
  border:2px solid #a7acb7;
  background:#efefef;
  border-radius:8px;
  cursor:pointer;
}
.ghost:disabled{
  opacity:.5;
  cursor:not-allowed;
}
.ghost:hover:not(:disabled){
  background:#e8e8e8;
}
@media (max-width: 720px){
  .thead,
  .trow{
    grid-template-columns:50px 1fr 80px;
  }
}
</style>
