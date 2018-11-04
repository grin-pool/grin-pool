import {
  ellipsizeString,
  getTokenInfoFromCurrencyCode,
  getTokenInfoFromAddress
} from './utils'
import { TestTubeEmptyIcon } from 'mdi-react';

test('Can get ZRX token info from currencyCode and directory', () => {
  const zrxInfo = {
    address: '0xE41d2489571d322189246DaFA5ebDe1F4699F498',
    symbol: 'ZRX',
    decimal: 18,
    type: 'default'               
  }
  const fakeState = {
    tokens: {
      tokensDirectory: [
        {
          address: '0x05f4a42e251f2d52b8ed15E9FEdAacFcEF1FAD27',
          symbol: 'ZIL',
          decimal: 12,
          type: 'default'    
        }, 
          zrxInfo
        ,{
        address: '0xe386b139ed3715ca4b18fd52671bdcea1cdfe4b1',
        symbol: 'ZST',
        decimal: 8,
        type: 'default'        
      }]
    }
  }
  expect(getTokenInfoFromCurrencyCode('ZRX', fakeState))
  .toBe(zrxInfo)
})

test('Can get ZRX token info from (uppercase) address and directory', () => {
  const zrxInfo = {
    address: '0xE41d2489571d322189246DaFA5ebDe1F4699F498',
    symbol: 'ZRX',
    decimal: 18,
    type: 'default'               
  }
  const fakeState = {
    tokens: {
      tokensDirectory: [
        {
          address: '0x05f4a42e251f2d52b8ed15E9FEdAacFcEF1FAD27',
          symbol: 'ZIL',
          decimal: 12,
          type: 'default'    
        }, 
          zrxInfo
        ,{
        address: '0xe386b139ed3715ca4b18fd52671bdcea1cdfe4b1',
        symbol: 'ZST',
        decimal: 8,
        type: 'default'        
      }]
    }
  }
  expect(getTokenInfoFromAddress('0xE41d2489571d322189246DaFA5ebDe1F4699F498', fakeState))
  .toBe(zrxInfo)
})

test('Can get ZRX token info from (lowercase) address and directory', () => {
  const zrxInfo = {
    address: '0xE41d2489571d322189246DaFA5ebDe1F4699F498',
    symbol: 'ZRX',
    decimal: 18,
    type: 'default'               
  }
  const fakeState = {
    tokens: {
      tokensDirectory: [
        {
          address: '0x05f4a42e251f2d52b8ed15E9FEdAacFcEF1FAD27',
          symbol: 'ZIL',
          decimal: 12,
          type: 'default'    
        }, 
          zrxInfo
        ,{
        address: '0xe386b139ed3715ca4b18fd52671bdcea1cdfe4b1',
        symbol: 'ZST',
        decimal: 8,
        type: 'default'        
      }]
    }
  }
  expect(getTokenInfoFromAddress('0xE41d2489571d322189246DaFA5ebDe1F4699F498'.toLowerCase(), fakeState))
  .toBe(zrxInfo)
})

