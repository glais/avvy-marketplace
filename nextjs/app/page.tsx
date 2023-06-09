import { Domain, columns } from "./components/columns"
import { DataTable } from "./components/data-table"
 

async function getData(): Promise<Domain[]> {
  const response = await fetch('http://127.0.0.1:5000/api/domains');
  return response.json();
}
 
export default async function Home() {
  const data = await getData()
  console.log(data)
 
  return (
    <div className="container mx-auto py-10">
      <DataTable columns={columns} data={data} />
    </div>
  )
}