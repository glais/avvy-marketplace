"use client"
 
import { ethers } from 'ethers'
import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
 
// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Domain = {
  DomainName: string
  ExpiryDate: string
  DomainStatus: string
}
 
export const columns: ColumnDef<Domain>[] = [
  {
    accessorKey: "DomainName",
    header: ({ column }) => {
      return (
        <Button variant="link" className="px-0" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Domain Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
  },
  {
    accessorKey: "DomainStatus",
    header: "Status"
  },
  {
    accessorKey: "ExpiryDate",
    header: "Expires"
  },
  {
    accessorFn: (row, index) => {
      let listings = ''
      let openseaPrice
      if (row['OpenseaPrice']) {
        openseaPrice = ethers.formatUnits(
          BigInt(row['OpenseaPrice']), 
          BigInt(row['OpenseaDecimals'])
        ) + ' ' + row['OpenseaCurrency']
        listings += `
          Opensea (${openseaPrice})
        `
      }
      return listings
    },
    header: 'Marketplace'
  }
]
