import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  withCredentials: true, // for session cookies
});

// Auth
export function login(email, password) {
  return api.post('/auth/login', { email, password });
}
export function logout() {
  return api.post('/auth/logout');
}
export function register(name, email, password) {
  return api.post('/auth/register', { name, email, password });
}
export function authTest() {
  return api.get('/auth/test');
}

// Users
export function getMe() {
  return api.get('/users/me');
}
export function updateGoals(goals) {
  return api.post('/users/goals', goals);
}
export function incrementQuizzes() {
  return api.post('/users/quizzes/completed');
}
export function getLibrary() {
  return api.get('/users/library');
}

// Articles
export function getArticle(id) {
  return api.get(`/articles/${id}`);
}
export function logReadingTime(id, data) {
  return api.post(`/articles/${id}/reading-time`, data);
}
export function searchArticles(params) {
  return api.get('/articles/search', { params });
}

// Quizzes
export function generateQuiz(data) {
  return api.post('/quizzes/generate', data);
}

// Translations
export function getTranslations(words) {
  return api.get('/translations', { params: { words } });
}

// Word Bank
export function addWord(word) {
  return api.post('/word', word);
}
export function deleteWord(id) {
  return api.delete(`/word/${id}`);
}
export function clearWords() {
  return api.delete('/words');
}