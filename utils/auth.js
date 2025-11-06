// Система аутентификации по ключам
const VALID_KEYS = [
  'AUTH-8f3a9b2c-1d4e-5f6a-7b8c-9d0e1f2a3b4c',
  'AUTH-2c4d6e8f-3a5b-7c9d-1e2f-4a6b8c0d2e4f',
  'AUTH-5e7f9a1b-2c3d-4e5f-6a7b-8c9d0e1f2a3b',
  'AUTH-9b1c3d5e-7f8a-2b4c-6d8e-0f2a4b6c8d0e',
  'AUTH-3d5e7f9a-1b2c-4d6e-8f0a-2b4c6d8e0f2a',
  'AUTH-6a8b0c2d-4e6f-8a0b-2c4d-6e8f0a2b4c6d',
  'AUTH-0f2a4b6c-8d0e-2f4a-6b8c-0d2e4f6a8b0c',
  'AUTH-4c6d8e0f-2a4b-6c8d-0e2f-4a6b8c0d2e4f',
  'AUTH-8e0f2a4b-6c8d-0e2f-4a6b-8c0d2e4f6a8b',
  'AUTH-2b4c6d8e-0f2a-4b6c-8d0e-2f4a6b8c0d2e',
  'AUTH-6d8e0f2a-4b6c-8d0e-2f4a-6b8c0d2e4f6a',
  'AUTH-a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6',
  'AUTH-c3d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8',
  'AUTH-e5f6a7b8-c9d0-e1f2-a3b4-c5d6e7f8a9b0',
  'AUTH-b8c9d0e1-f2a3-b4c5-d6e7-f8a9b0c1d2e3',
  'AUTH-d0e1f2a3-b4c5-d6e7-f8a9-b0c1d2e3f4a5',
  'AUTH-f2a3b4c5-d6e7-f8a9-b0c1-d2e3f4a5b6c7',
  'AUTH-a3b4c5d6-e7f8-a9b0-c1d2-e3f4a5b6c7d8',
  'AUTH-c5d6e7f8-a9b0-c1d2-e3f4-a5b6c7d8e9f0',
  'AUTH-e7f8a9b0-c1d2-e3f4-a5b6-c7d8e9f0a1b2',
  'AUTH-b0c1d2e3-f4a5-b6c7-d8e9-f0a1b2c3d4e5',
  'AUTH-d2e3f4a5-b6c7-d8e9-f0a1-b2c3d4e5f6a7',
  'AUTH-f4a5b6c7-d8e9-f0a1-b2c3-d4e5f6a7b8c9',
  'AUTH-a5b6c7d8-e9f0-a1b2-c3d4-e5f6a7b8c9d0',
  'AUTH-c7d8e9f0-a1b2-c3d4-e5f6-a7b8c9d0e1f2',
  'AUTH-e9f0a1b2-c3d4-e5f6-a7b8-c9d0e1f2a3b4',
  'AUTH-b2c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7',
  'AUTH-d4e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9',
  'AUTH-f6a7b8c9-d0e1-f2a3-b4c5-d6e7f8a9b0c1',
  'AUTH-a7b8c9d0-e1f2-a3b4-c5d6-e7f8a9b0c1d2',
  'AUTH-c9d0e1f2-a3b4-c5d6-e7f8-a9b0c1d2e3f4',
  'AUTH-e1f2a3b4-c5d6-e7f8-a9b0-c1d2e3f4a5b6',
  'AUTH-b4c5d6e7-f8a9-b0c1-d2e3-f4a5b6c7d8e9',
  'AUTH-d6e7f8a9-b0c1-d2e3-f4a5-b6c7d8e9f0a1',
  'AUTH-f8a9b0c1-d2e3-f4a5-b6c7-d8e9f0a1b2c3',
  'AUTH-a9b0c1d2-e3f4-a5b6-c7d8-e9f0a1b2c3d4',
  'AUTH-c1d2e3f4-a5b6-c7d8-e9f0-a1b2c3d4e5f6',
  'AUTH-e3f4a5b6-c7d8-e9f0-a1b2-c3d4e5f6a7b8',
  'AUTH-b6c7d8e9-f0a1-b2c3-d4e5-f6a7b8c9d0e1',
  'AUTH-d8e9f0a1-b2c3-d4e5-f6a7-b8c9d0e1f2a3',
  'AUTH-f0a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5',
  'AUTH-a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6',
  'AUTH-c3d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8',
  'AUTH-e5f6a7b8-c9d0-e1f2-a3b4-c5d6e7f8a9b0',
  'AUTH-b8c9d0e1-f2a3-b4c5-d6e7-f8a9b0c1d2e3',
  'AUTH-d0e1f2a3-b4c5-d6e7-f8a9-b0c1d2e3f4a5',
  'AUTH-f2a3b4c5-d6e7-f8a9-b0c1-d2e3f4a5b6c7',
  'AUTH-a3b4c5d6-e7f8-a9b0-c1d2-e3f4a5b6c7d8',
  'AUTH-c5d6e7f8-a9b0-c1d2-e3f4-a5b6c7d8e9f0',
  'AUTH-e7f8a9b0-c1d2-e3f4-a5b6-c7d8e9f0a1b2',
  'AUTH-b0c1d2e3-f4a5-b6c7-d8e9-f0a1b2c3d4e5',
  'AUTH-d2e3f4a5-b6c7-d8e9-f0a1-b2c3d4e5f6a7',
  'AUTH-f4a5b6c7-d8e9-f0a1-b2c3-d4e5f6a7b8c9',
  'AUTH-a5b6c7d8-e9f0-a1b2-c3d4-e5f6a7b8c9d0',
  'AUTH-c7d8e9f0-a1b2-c3d4-e5f6-a7b8c9d0e1f2',
  'AUTH-e9f0a1b2-c3d4-e5f6-a7b8-c9d0e1f2a3b4',
  'AUTH-b2c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7',
  'AUTH-d4e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9',
  'AUTH-f6a7b8c9-d0e1-f2a3-b4c5-d6e7f8a9b0c1',
  'AUTH-a7b8c9d0-e1f2-a3b4-c5d6-e7f8a9b0c1d2',
  'AUTH-c9d0e1f2-a3b4-c5d6-e7f8-a9b0c1d2e3f4',
  'AUTH-e1f2a3b4-c5d6-e7f8-a9b0-c1d2e3f4a5b6',
  'AUTH-b4c5d6e7-f8a9-b0c1-d2e3-f4a5b6c7d8e9',
  'AUTH-d6e7f8a9-b0c1-d2e3-f4a5-b6c7d8e9f0a1',
  'AUTH-f8a9b0c1-d2e3-f4a5-b6c7-d8e9f0a1b2c3',
  'AUTH-a9b0c1d2-e3f4-a5b6-c7d8-e9f0a1b2c3d4',
  'AUTH-c1d2e3f4-a5b6-c7d8-e9f0-a1b2c3d4e5f6',
  'AUTH-e3f4a5b6-c7d8-e9f0-a1b2-c3d4e5f6a7b8',
  'AUTH-b6c7d8e9-f0a1-b2c3-d4e5-f6a7b8c9d0e1',
  'AUTH-d8e9f0a1-b2c3-d4e5-f6a7-b8c9d0e1f2a3',
  'AUTH-f0a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5',
  'AUTH-1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d',
  'AUTH-3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f',
  'AUTH-5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b',
  'AUTH-7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d',
  'AUTH-9c0d1e2f-3a4b-5c6d-7e8f-9a0b1c2d3e4f',
  'AUTH-1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6b',
  'AUTH-3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d',
  'AUTH-5c6d7e8f-9a0b-1c2d-3e4f-5a6b7c8d9e0f',
  'AUTH-7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b',
  'AUTH-9a0b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c4d',
  'AUTH-1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f',
  'AUTH-3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b',
  'AUTH-5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d',
  'AUTH-7c8d9e0f-1a2b-3c4d-5e6f-7a8b9c0d1e2f',
  'AUTH-9e0f1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b',
  'AUTH-1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d',
  'AUTH-2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e',
  'AUTH-4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a',
  'AUTH-6f7a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c',
  'AUTH-8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e',
  'AUTH-0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5a',
  'AUTH-2f3a4b5c-6d7e-8f9a-0b1c-2d3e4f5a6b7c',
  'AUTH-4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e',
  'AUTH-6d7e8f9a-0b1c-2d3e-4f5a-6b7c8d9e0f1a',
  'AUTH-8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c',
  'AUTH-0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e',
  'AUTH-2d3e4f5a-6b7c-8d9e-0f1a-2b3c4d5e6f7a',
  'AUTH-4f5a6b7c-8d9e-0f1a-2b3c-4d5e6f7a8b9c',
  'AUTH-6b7c8d9e-0f1a-2b3c-4d5e-6f7a8b9c0d1e',
  'AUTH-8d9e0f1a-2b3c-4d5e-6f7a-8b9c0d1e2f3a',
  'AUTH-0f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c',
  'AUTH-2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e',
  'AUTH-4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a',
  'AUTH-6f7a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c',
  'AUTH-8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e',
  'AUTH-0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5a',
  'AUTH-2f3a4b5c-6d7e-8f9a-0b1c-2d3e4f5a6b7c',
  'AUTH-4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e',
  'AUTH-6d7e8f9a-0b1c-2d3e-4f5a-6b7c8d9e0f1a',
  'AUTH-8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c',
  'AUTH-0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e',
  'AUTH-2d3e4f5a-6b7c-8d9e-0f1a-2b3c4d5e6f7a',
  'AUTH-4f5a6b7c-8d9e-0f1a-2b3c-4d5e6f7a8b9c',
  'AUTH-6b7c8d9e-0f1a-2b3c-4d5e-6f7a8b9c0d1e',
  'AUTH-8d9e0f1a-2b3c-4d5e-6f7a-8b9c0d1e2f3a',
  'AUTH-0f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c',
  'AUTH-a2b4c6d8-e0f2-a4b6-c8d0-e2f4a6b8c0d2',
  'AUTH-c4d6e8f0-a2b4-c6d8-e0f2-a4b6c8d0e2f4',
  'AUTH-e6f8a0b2-c4d6-e8f0-a2b4-c6d8e0f2a4b6',
  'AUTH-b8c0d2e4-f6a8-b0c2-d4e6-f8a0b2c4d6e8',
  'AUTH-d0e2f4a6-b8c0-d2e4-f6a8-b0c2d4e6f8a0',
  'AUTH-f2a4b6c8-d0e2-f4a6-b8c0-d2e4f6a8b0c2',
  'AUTH-a4b6c8d0-e2f4-a6b8-c0d2-e4f6a8b0c2d4',
  'AUTH-c6d8e0f2-a4b6-c8d0-e2f4-a6b8c0d2e4f6',
  'AUTH-e8f0a2b4-c6d8-e0f2-a4b6-c8d0e2f4a6b8',
  'AUTH-b0c2d4e6-f8a0-b2c4-d6e8-f0a2b4c6d8e0',
  'AUTH-d2e4f6a8-b0c2-d4e6-f8a0-b2c4d6e8f0a2',
  'AUTH-f4a6b8c0-d2e4-f6a8-b0c2-d4e6f8a0b2c4',
  'AUTH-a6b8c0d2-e4f6-a8b0-c2d4-e6f8a0b2c4d6',
  'AUTH-c8d0e2f4-a6b8-c0d2-e4f6-a8b0c2d4e6f8',
  'AUTH-e0f2a4b6-c8d0-e2f4-a6b8-c0d2e4f6a8b0',
  'AUTH-b2c4d6e8-f0a2-b4c6-d8e0-f2a4b6c8d0e2',
  'AUTH-d4e6f8a0-b2c4-d6e8-f0a2-b4c6d8e0f2a4',
  'AUTH-f6a8b0c2-d4e6-f8a0-b2c4-d6e8f0a2b4c6',
  'AUTH-a8b0c2d4-e6f8-a0b2-c4d6-e8f0a2b4c6d8',
  'AUTH-c0d2e4f6-a8b0-c2d4-e6f8-a0b2c4d6e8f0',
  'AUTH-e2f4a6b8-c0d2-e4f6-a8b0-c2d4e6f8a0b2',
  'AUTH-b4c6d8e0-f2a4-b6c8-d0e2-f4a6b8c0d2e4',
  'AUTH-d6e8f0a2-b4c6-d8e0-f2a4-b6c8d0e2f4a6',
  'AUTH-f8a0b2c4-d6e8-f0a2-b4c6-d8e0f2a4b6c8',
  'AUTH-a0b2c4d6-e8f0-a2b4-c6d8-e0f2a4b6c8d0',
  'AUTH-c2d4e6f8-a0b2-c4d6-e8f0-a2b4c6d8e0f2',
  'AUTH-e4f6a8b0-c2d4-e6f8-a0b2-c4d6e8f0a2b4',
  'AUTH-b6c8d0e2-f4a6-b8c0-d2e4-f6a8b0c2d4e6',
  'AUTH-d8e0f2a4-b6c8-d0e2-f4a6-b8c0d2e4f6a8',
  'AUTH-f0a2b4c6-d8e0-f2a4-b6c8-d0e2f4a6b8c0',
  'AUTH-a2b4c6d8-e0f2-a4b6-c8d0-e2f4a6b8c0d2',
  'AUTH-c4d6e8f0-a2b4-c6d8-e0f2-a4b6c8d0e2f4',
  'AUTH-e6f8a0b2-c4d6-e8f0-a2b4-c6d8e0f2a4b6',
  'AUTH-b8c0d2e4-f6a8-b0c2-d4e6-f8a0b2c4d6e8',
  'AUTH-d0e2f4a6-b8c0-d2e4-f6a8-b0c2d4e6f8a0',
  'AUTH-f2a4b6c8-d0e2-f4a6-b8c0-d2e4f6a8b0c2',
  'AUTH-a4b6c8d0-e2f4-a6b8-c0d2-e4f6a8b0c2d4',
  'AUTH-c6d8e0f2-a4b6-c8d0-e2f4-a6b8c0d2e4f6',
  'AUTH-e8f0a2b4-c6d8-e0f2-a4b6-c8d0e2f4a6b8',
  'AUTH-b0c2d4e6-f8a0-b2c4-d6e8-f0a2b4c6d8e0',
  'AUTH-d2e4f6a8-b0c2-d4e6-f8a0-b2c4d6e8f0a2',
  'AUTH-f4a6b8c0-d2e4-f6a8-b0c2-d4e6f8a0b2c4',
  'AUTH-a6b8c0d2-e4f6-a8b0-c2d4-e6f8a0b2c4d6',
  'AUTH-c8d0e2f4-a6b8-c0d2-e4f6-a8b0c2d4e6f8',
  'AUTH-e0f2a4b6-c8d0-e2f4-a6b8-c0d2e4f6a8b0',
  'AUTH-b2c4d6e8-f0a2-b4c6-d8e0-f2a4b6c8d0e2',
  'AUTH-d4e6f8a0-b2c4-d6e8-f0a2-b4c6d8e0f2a4',
  'AUTH-f6a8b0c2-d4e6-f8a0-b2c4-d6e8f0a2b4c6',
  'AUTH-a8b0c2d4-e6f8-a0b2-c4d6-e8f0a2b4c6d8',
  'AUTH-c0d2e4f6-a8b0-c2d4-e6f8-a0b2c4d6e8f0',
  'AUTH-e2f4a6b8-c0d2-e4f6-a8b0-c2d4e6f8a0b2',
  'AUTH-b4c6d8e0-f2a4-b6c8-d0e2-f4a6b8c0d2e4',
  'AUTH-d6e8f0a2-b4c6-d8e0-f2a4-b6c8d0e2f4a6',
  'AUTH-f8a0b2c4-d6e8-f0a2-b4c6-d8e0f2a4b6c8',
  'AUTH-a0b2c4d6-e8f0-a2b4-c6d8-e0f2a4b6c8d0',
  'AUTH-c2d4e6f8-a0b2-c4d6-e8f0-a2b4c6d8e0f2',
  'AUTH-e4f6a8b0-c2d4-e6f8-a0b2-c4d6e8f0a2b4',
  'AUTH-b6c8d0e2-f4a6-b8c0-d2e4-f6a8b0c2d4e6',
  'AUTH-d8e0f2a4-b6c8-d0e2-f4a6-b8c0d2e4f6a8',
  'AUTH-f0a2b4c6-d8e0-f2a4-b6c8-d0e2f4a6b8c0',
  'AUTH-9f1e3d5c-7b2a-4869-0e5f-1d3c5a7b9e0f',
  'AUTH-1d3c5a7b-9e0f-2d4c-6a8b-0e2f4d6a8c0e',
  'AUTH-5a7b9e0f-1d3c-5a7b-9e0f-1d3c5a7b9e0f',
  'AUTH-7b9e0f1d-3c5a-7b9e-0f1d-3c5a7b9e0f1d',
  'AUTH-9e0f1d3c-5a7b-9e0f-1d3c-5a7b9e0f1d3c',
  'AUTH-0f1d3c5a-7b9e-0f1d-3c5a-7b9e0f1d3c5a',
  'AUTH-1d3c5a7b-9e0f-1d3c-5a7b-9e0f1d3c5a7b',
  'AUTH-3c5a7b9e-0f1d-3c5a-7b9e-0f1d3c5a7b9e',
  'AUTH-5a7b9e0f-1d3c-5a7b-9e0f-1d3c5a7b9e0f',
  'AUTH-7b9e0f1d-3c5a-7b9e-0f1d-3c5a7b9e0f1d',
  'AUTH-9e0f1d3c-5a7b-9e0f-1d3c-5a7b9e0f1d3c',
  'AUTH-0f1d3c5a-7b9e-0f1d-3c5a-7b9e0f1d3c5a',
  'AUTH-1d3c5a7b-9e0f-1d3c-5a7b-9e0f1d3c5a7b',
  'AUTH-3c5a7b9e-0f1d-3c5a-7b9e-0f1d3c5a7b9e',
  'AUTH-5a7b9e0f-1d3c-5a7b-9e0f-1d3c5a7b9e0f',
  'AUTH-7b9e0f1d-3c5a-7b9e-0f1d-3c5a7b9e0f1d',
  'AUTH-9e0f1d3c-5a7b-9e0f-1d3c-5a7b9e0f1d3c',
  'AUTH-0f1d3c5a-7b9e-0f1d-3c5a-7b9e0f1d3c5a',
  'AUTH-1d3c5a7b-9e0f-1d3c-5a7b-9e0f1d3c5a7b',
  'AUTH-3c5a7b9e-0f1d-3c5a-7b9e-0f1d3c5a7b9e'
];

class AuthManager {
  constructor() {
    this.authenticated = false;
    this.currentKey = null;
  }

  async validateKey(key) {
    if (!key || typeof key !== 'string') {
      return false;
    }
    
    const trimmedKey = key.trim();
    return VALID_KEYS.includes(trimmedKey);
  }

  async authenticate(key) {
    const isValid = await this.validateKey(key);
    if (isValid) {
      this.authenticated = true;
      this.currentKey = key.trim();
      await this.saveAuthState();
      return true;
    }
    return false;
  }

  async saveAuthState() {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      await chrome.storage.local.set({
        authenticated: this.authenticated,
        authKey: this.currentKey
      });
    }
  }

  async loadAuthState() {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      const result = await chrome.storage.local.get(['authenticated', 'authKey']);
      if (result.authenticated && result.authKey) {
        const isValid = await this.validateKey(result.authKey);
        if (isValid) {
          this.authenticated = true;
          this.currentKey = result.authKey;
          return true;
        }
      }
    }
    return false;
  }

  async logout() {
    this.authenticated = false;
    this.currentKey = null;
    if (typeof chrome !== 'undefined' && chrome.storage) {
      await chrome.storage.local.remove(['authenticated', 'authKey']);
    }
  }

  isAuthenticated() {
    return this.authenticated;
  }
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AuthManager;
}
