import Layout from 'app/layout'
import { Domain, columns } from "app/components/columns"
import { DataTable } from "app/components/data-table"
import { useRouter } from 'next/router'

import { useEffect, useState } from 'react'
 

async function getData(slug): Domain[] {
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/collections/${slug}/`
  const response = await fetch(url, { cache: 'no-store' });
  const body = await response.json()
  console.log(body)
  return body.data;
}
 
export default async function Page() {
  const data = await getData('first-names')
 
  return (
    <Layout>
      <div className="container mx-auto py-10">
        <DataTable columns={columns} data={data} />
      </div>
    </Layout>
  )
}
