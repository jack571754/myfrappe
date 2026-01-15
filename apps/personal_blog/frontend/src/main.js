import { createApp } from 'vue'
import { FrappeUI, setConfig, frappeRequest } from 'frappe-ui'
import App from './App.vue'
import router from './router'
import './index.css'

// 使用 frappe-ui 原生请求方法
setConfig('resourceFetcher', frappeRequest)

const app = createApp(App)

app.use(FrappeUI)
app.use(router)

app.mount('#blog-app')
