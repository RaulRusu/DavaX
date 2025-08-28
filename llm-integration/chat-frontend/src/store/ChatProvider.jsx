import React, { createContext, useContext, useReducer, useMemo, useCallback, useEffect } from 'react'
import * as api from '../lib/api.js'

const ChatContext = createContext(null)

const initialState = {
  chats: [],
  activeId: null,
  messages: {},
  loading: false,
  error: null
}

function reducer(state, action) {
  switch (action.type) {
    case 'LOAD_START':
      return { ...state, loading: true, error: null }
    case 'LOAD_SUCCESS': {
      const { chats } = action.payload
      const activeId = chats[0]?.id ?? null
      return { ...state, loading: false, chats, activeId }
    }
    case 'LOAD_MESSAGES_SUCCESS': {
      const { chatId, messages } = action.payload
      return { ...state, messages: { ...state.messages, [chatId]: messages } }
    }
    case 'SELECT_CHAT':
      return { ...state, activeId: action.payload }
    case 'CREATE_CHAT_SUCCESS': {
      const chat = action.payload
      return {
        ...state,
        chats: [chat, ...state.chats],
        activeId: chat.id,
        messages: { ...state.messages, [chat.id]: [] }
      }
    }
    case 'ADD_MESSAGE': {
      const { chatId, message } = action.payload
      const list = state.messages[chatId] || []
      return { ...state, messages: { ...state.messages, [chatId]: [...list, message] } }
    }
    case 'REPLACE_LAST_MESSAGE': {
      const { chatId, message } = action.payload
      const list = state.messages[chatId] || []
      const copy = list.slice()
      copy[copy.length - 1] = message
      return { ...state, messages: { ...state.messages, [chatId]: copy } }
    }
    case 'ERROR':
      return { ...state, loading: false, error: action.payload }
    default:
      return state
  }
}

// helper to make a reasonable title from user input
const makeTitle = (s) => {
  const t = (s || '').trim().replace(/\s+/g, ' ')
  return t.length ? t.slice(0, 60) : 'New chat'
}

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  useEffect(() => {
    (async () => {
      try {
        dispatch({ type: 'LOAD_START' })
        const chats = await api.listChats()
        dispatch({ type: 'LOAD_SUCCESS', payload: { chats } })
        const firstId = chats[0]?.id
        if (firstId) {
          const messages = await api.listMessages(firstId)
          dispatch({ type: 'LOAD_MESSAGES_SUCCESS', payload: { chatId: firstId, messages } })
        }
      } catch (e) {
        dispatch({ type: 'ERROR', payload: e?.message || 'Failed to load' })
      }
    })()
  }, [])

  // now accepts an optional title
  const createChat = useCallback(async (title = 'New chat') => {
    try {
      const chat = await api.createChat(title)
      dispatch({ type: 'CREATE_CHAT_SUCCESS', payload: chat })
      return chat
    } catch (e) {
      dispatch({ type: 'ERROR', payload: e?.message || 'Failed to create chat' })
      throw e
    }
  }, [])

  const selectChat = useCallback(async (chatId) => {
    dispatch({ type: 'SELECT_CHAT', payload: chatId })
    if (!state.messages[chatId]) {
      try {
        const messages = await api.listMessages(chatId)
        dispatch({ type: 'LOAD_MESSAGES_SUCCESS', payload: { chatId, messages } })
      } catch (e) {
        dispatch({ type: 'ERROR', payload: e?.message || 'Failed to load messages' })
      }
    }
  }, [state.messages])

  const sendMessage = useCallback(async (content) => {
    try {
      let chatId = state.activeId
      // if no chat selected, create one using the first message as the title
      if (!chatId) {
        const chat = await createChat(makeTitle(content))
        chatId = chat.id
      }
      const userMsg = {
        id: 'local-' + Date.now(),
        role: 'user',
        event_type: "message_text",
        createdAt: new Date().toISOString(),
        pending: true,
        chat_id: chatId,
        payload: { content }
      }
      dispatch({ type: 'ADD_MESSAGE', payload: { chatId, message: userMsg } })

      const assistantMsg = await api.sendMessage(chatId, content)
      dispatch({
        type: 'REPLACE_LAST_MESSAGE',
        payload: { chatId, message: { ...userMsg, pending: false } }
      })
      //dispatch({ type: 'ADD_MESSAGE', payload: { chatId, message: assistantMsg } })

      const messages = await api.listMessages(chatId)
      dispatch({ type: 'LOAD_MESSAGES_SUCCESS', payload: { chatId, messages } })
    } catch (e) {
      dispatch({ type: 'ERROR', payload: e?.message || 'Failed to send message' })
    }
  }, [state.activeId, createChat])

  const value = useMemo(() => ({
    ...state,
    selectChat,
    createChat,
    sendMessage
  }), [state, selectChat, createChat, sendMessage])

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export function useChat() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error('useChat must be used within ChatProvider')
  return ctx
}
