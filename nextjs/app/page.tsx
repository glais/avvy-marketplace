import Layout from 'app/layout'
import { ethers } from 'ethers'
import { Domain, columns } from "app/components/columns"
import { DataTable } from "app/components/data-table"
import { useRouter } from 'next/router'

import { useEffect, useState } from 'react'
 
export type CollectionResponse = {
  name: string,
  domains: Domain[]
}

async function getData(slug): CollectionResponse {
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/collections/${slug}/`
  const response = await fetch(url, { cache: 'no-store' });
  const body = await response.json()
  return body;
}
 
export default async function Page() {

  // slug should be loaded from url
  const slug = 'opensea-english-words'
  //const slug = 'first-names'
  const data = await getData(slug)

  const formatAVAX = (row) => {
    return ethers.formatUnits(
      BigInt(row['OpenseaPrice']), 
      BigInt(row['OpenseaDecimals'])
    ) + ' ' + row['OpenseaCurrency']
  }

  const getFloorPrice = (items) => {
    return formatAVAX(items.reduce((sum, curr) => {
      if (!sum || curr.OpenseaPrice < sum.OpenseaPrice) return curr
      return sum
    }, null))
  }

  const saleItems = data.domains.filter((d) => d.DomainStatus === 'For Sale')
 
  return (
    <Layout>
      <div className="container mx-auto py-10">
        <div className='mb-4 text-lg font-bold'>
          {data.name}
        </div>
        <div className='border border-gray-200 p-4 rounded text-sm mb-4'>
          <div className='font-semibold'>Stats</div>
          <div className='flex items-center'>
            <div className='pr-4'>Total Items: {data.domains.length}</div>
            <div className='pr-4'>Available: {data.domains.filter((d) => d.DomainStatus === 'Available').length}</div>
            <div className='pr-4'>Registered: {data.domains.filter((d) => d.DomainStatus === 'Registered').length}</div>
            <div className='pr-4'>For Sale: {saleItems.length}</div>
            <div className='pr-4'>Floor Price: {getFloorPrice(saleItems)}</div>
          </div>
        </div>
        <DataTable columns={columns} data={data.domains} />
      </div>
    </Layout>
  )
}
