from django.shortcuts import redirect, render
from django.contrib import messages
import requests
from datetime import datetime
import pandas as pd
from django.http import FileResponse, HttpResponse
import csv
from .forms import CSVUploadForm
from django.shortcuts import render

def index(request):
    return redirect('/auth/login')

def dashboard(request, id):
    if(request.method == 'GET'):
        messages.info(request, "")
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        poDetails = requests.get(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/getpolist?CompanyId={id}", headers=headers).json()['data']
        return render(request, 'dashboard/dashboard.html', {'po': len(poDetails), 'id': id, 'data': 0})
            
    else:
        messages.info(request, "Something went Wrong")
        return render(request, 'index.html')
    

def poDetails(request, id):
    if(request.method == 'GET'):
        messages.info(request, "")
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        poDetails = requests.get(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/getpolist?CompanyId={id}", headers=headers).json()['data']
        
        # df = pd.DataFrame(poDetails)
        # df.to_csv('poDetails.csv')
        # print("Excel File Generated Successfully!!")
        
        poDetailsMain = []

        for po in poDetails:
            potype = ""
            if(po['PoType'] == 101):
                potype = "Open"

            elif(po['PoType'] == 102):
                potype = "One Time"

            leng = len(po['PoNo'])
            poDetailsMain.append({'PoNo': po['PoNo'][ leng - 5: ], 
                                  'PoAmend': po['PoAmend'],
                                  'PoDate': po['PoDate'],
                                  'PoType' : potype,
                                  'MaterialCode' : po['MaterialCode'],
                                  'Uom': po['Uom'],
                                  'Rate': po['Rate'],
                                  'PoQty': po['PoQty'],
                                  'MaterialName': po['MaterialName'],
                                  'PendQty': po['PendQty']
                                  })
        
        return render(request, 'dashboard/poDetails.html', {'data': poDetailsMain, 'id': id})
            
    else:
        messages.info(request, "Something went Wrong")
        return render(request, 'index.html')


def grnDetails(request, id):
    if(request.method == 'GET'):
        messages.info(request, "")
        return render(request, 'dashboard/grnDetails.html', {'id': id})
            
    else:
        messages.info(request, "")
        fromDate = request.POST['fromdate']
        toDate = request.POST['todate']
        fDate = datetime.strptime(fromDate, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        tDate = datetime.strptime(toDate, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        grnDetails = requests.get(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/getgrnlist?CompanyId={id}&FromDate={fDate}&ToDate={tDate}", headers=headers).json()['data']
        # df = pd.DataFrame(grnDetails)
        # df.to_csv('grnDetails.csv')
        # print("Excel File Generated Successfully!!")

        grnDetailsMain = []

        for grn in grnDetails:
            leng = len(grn['ShortTrnNo'])
            grnDetailsMain.append({'ShortTrnNo': grn['ShortTrnNo'][ leng - 6: ], 
                                  'SubGlAcNo': grn['SubGlAcNo'],
                                  'TrnDate': grn['TrnDate'],
                                  'MaterialCode' : grn['MaterialCode'],
                                  'Quantity': grn['Quantity'],
                                  'MaterialName': grn['MaterialName'],
                                  'MaterialUom': grn['MaterialUom']
                                  })

        return render(request, 'dashboard/grnDetails.html', {'id': id, 'data': grnDetailsMain, 'fromDate': fromDate, 'toDate': toDate})

def gstDetails(request, id):
    if(request.method == 'GET'):
        messages.info(request, "")
        return render(request, 'dashboard/gstDetails.html', {'id': id})
    
    elif(request.method == "POST" and request.POST['download']=="download"):
       
        messages.info(request, "")
        fromDate = request.POST['fromdate']
        toDate = request.POST['todate']
        fDate = datetime.strptime(fromDate, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        tDate = datetime.strptime(toDate, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        gstDetails = requests.get(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/getgstrtnstatus?CompanyId={id}&FromDate={fDate}&ToDate={tDate}", headers=headers).json()['data']

        response = HttpResponse(
            content_type="text/csv",
            # headers={"Content-Disposition": f'attachment; filename="gstdata.csv"'},
            headers={"Content-Disposition": f'attachment; filename="gst-return-{fDate}-{tDate}-{id}.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(['GstIn of Supplier','Trade/Legal name of the Supplier','TrnNO','TrnDate' ,'Invoice Number','Invoice Date','Invoice Value','Place of Supply','Rate (%)','Taxable Value','Integrated Tax','Central Tax', 'State/UT Tax','Status', 'GstIn of Supplier','Trade/Legal name of the Supplier', 'TrnNO','TrnDate', 'Invoice Number', 'Invoice Date', 'Invoice Value','Place of Supply', 'Rate (%)','Taxable Value','Integrated Tax','Central Tax','State/UT Tax'])

        gstDetailsMain = []

        for gst in gstDetails:
        
            leng = len(gst['StrTrnNo'])
            gstBillDate = gst['PartyBillDate']
            billdate = ""
            if(gstBillDate==None):
                billdate = "None"
            else:
                billdate = f"{gstBillDate[6:]}/{gstBillDate[4:6]}/{gstBillDate[0:4]}"
            
            gsttrnDate = gst['TrnDate']
            trndate = ""
            if(gsttrnDate==None):
                trndate = "None"
            else:
                trndate = f"{gsttrnDate[6:]}/{gsttrnDate[4:6]}/{gsttrnDate[0:4]}"
            

            gstDetailsMain.append({'GstIn of Supplier': gst['GstIn'],
                                'Trade/Legal name of the Supplier': gst['LongName'], 
                                  'TrnNO': gst['TrnNO'],
                                  'TrnDate' : gst['TrnDate'],
                                  'Invoice Number' : gst['PortalInvoiceNo'],
                                  'Invoice Date' : gst['PortalInvoiceDate'],
                                  'Invoice Value' : gst['SysInvoiceValue'],
                                  'Place of Supply' : gst['SysStateName'],
                                  'Rate (%)' : gst['SysRate'],
                                  'Taxable Value' : gst['SysTaxableValue'],
                                  'Integrated Tax' : gst['SysIGstAmt'],
                                  'Central Tax' : gst['SysCGstAmt'],
                                  'State/UT Tax' : gst['SysSGstAmt'],
                                  'Status' : gst['MatchStatus'],

                                  'GstIn of Supplier': gst['PortalGstIn'],
                                'Trade/Legal name of the Supplier': gst['PortalLongName'], 
                                  'TrnNO': gst['TrnNO'],
                                  'TrnDate' : gst['PortalTrnDate'],
                                  'Invoice Number' : gst['PortalInvoiceNo'],
                                  'Invoice Date' : gst['PortalInvoiceDate'],
                                  'Invoice Value' : gst['PortalInvoiceValue'],
                                  'Place of Supply' : gst['SysStateName'],
                                  'Rate (%)' : gst['PortalRate'],
                                  'Taxable Value' : gst['PortalTaxableValue'],
                                  'Integrated Tax' : gst['PortalIGstAmt'],
                                  'Central Tax' : gst['PortalCGstAmt'],
                                  'State/UT Tax' : gst['PortalSGstAmt']
                                  })
            
            writer.writerow([gst['GstIn'],gst['LongName'],gst['TrnNO'],gst['TrnDate'],gst['PortalInvoiceNo'],gst['PortalInvoiceDate'],gst['SysInvoiceValue'],gst['SysStateName'],gst['SysRate'],gst['SysTaxableValue'],gst['SysIGstAmt'],gst['SysCGstAmt'],gst['SysSGstAmt'],gst['MatchStatus'],gst['PortalGstIn'],gst['PortalLongName'],gst['TrnNO'],gst['PortalTrnDate'], gst['PortalInvoiceNo'],gst['PortalInvoiceDate'], gst['PortalInvoiceValue'], gst['SysStateName'], gst['PortalRate'], gst['PortalTaxableValue'], gst['PortalIGstAmt'],['PortalCGstAmt'],gst['PortalSGstAmt']])

        return response
        # print("Excel File Generated Successfully!!")

        # return render(request, 'dashboard/gstDetails.html', {'id': id, 'data': gstDetailsMain})

    else:
        messages.info(request, "")
        fromDate = request.POST['fromdate']
        toDate = request.POST['todate']
        fDate = datetime.strptime(fromDate, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        tDate = datetime.strptime(toDate, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        gstDetails = requests.get(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/getgstrtnstatus?CompanyId={id}&FromDate={fDate}&ToDate={tDate}", headers=headers).json()['data']
        # df = pd.DataFrame(gstDetails)
        # df.to_csv('gstDetails.csv')
        # print("Excel File Generated Successfully!!")

        gstDetailsMain = []
        # print(gstDetails)

        for gst in gstDetails:
        
            leng = len(gst['StrTrnNo'])
            gstBillDate = gst['PartyBillDate']
            billdate = ""
            if(gstBillDate==None):
                billdate = "None"
            else:
                billdate = f"{gstBillDate[6:]}/{gstBillDate[4:6]}/{gstBillDate[0:4]}"
            
            gsttrnDate = gst['TrnDate']
            trndate = ""
            if(gsttrnDate==None):
                trndate = "None"
            else:
                trndate = f"{gsttrnDate[6:]}/{gsttrnDate[4:6]}/{gsttrnDate[0:4]}"

            gstDetailsMain.append({'LongName': gst['LongName'], 
                                  'PartyBillNo': gst['PartyBillNo'],
                                  'PartyBillDate': billdate,
                                  'TrnDate' : trndate,
                                  'TrnNO': gst['StrTrnNo'][leng - 6:],
                                  'SysTaxableValue': gst['SysTaxableValue'],
                                  'SysCGstAmt': gst['SysCGstAmt'],
                                  'SysSGstAmt': gst['SysSGstAmt'],
                                  'SysIGstAmt': gst['SysIGstAmt'],
                                  'SysInvoiceValue': gst['SysInvoiceValue'],
                                  'SysRate': gst['SysRate']
                                  })

        return render(request, 'dashboard/gstDetails.html', {'id': id, 'data': gstDetailsMain, 'fromDate': fromDate, 'toDate': toDate})

def scheduleDetails(request, id):
    if(request.method == 'GET'):
        messages.info(request, "")
        return render(request, 'dashboard/scheduleList.html', {'id': id})
            
    else:
        messages.info(request, "")
        fromDate = request.POST['fromdate']
        fDate = datetime.strptime(fromDate, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        scheduleDetails = requests.get(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/getshedule?CompanyId={id}&Month={fDate}", headers=headers).json()['data']
        # df = pd.DataFrame(scheduleDetails)
        # df.to_csv('scheduleDetails.csv')
        # print("Excel File Generated Successfully!!")
        return render(request, 'dashboard/scheduleList.html', {'id': id, 'data': scheduleDetails, 'fromDate': fromDate})


def downloadAsn(request, id):
    if(request.method == "POST" and request.POST['download_asn']=="download_asn"):
        messages.info(request, "")
        
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="asn_template.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(["CompanyId", "VendorCode", "PoNo", "ItemNo","Quantity","VendorChallenNo","ChallenDate","NetPoRate","BasicAmount","TaxableAmount","CgstAmount","SgstAmount","IgstAmount","CgstRate","SgstRate","IgstRate","InvoiceValue","Gstin","VehicleNo","TransporterName","IrnNo"])

        return response


def uploadAsn(request, id):
    uploadDetails = []
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']

        df = pd.read_csv(csv_file)
        # print(df)

        arr = []

        def uploadData(row):
            obj = {
                "CompanyId": row["CompanyId"],
                "VendorCode": row["VendorCode"],
                "PoNo": row["PoNo"], 
                "ItemNo":row["ItemNo"],
                "Quantity":row["Quantity"],
                "VendorChallenNo":row["VendorChallenNo"],
                "ChallenDate":row["ChallenDate"],
                "NetPoRate":row["NetPoRate"],
                "BasicAmount":row["BasicAmount"],
                "TaxableAmount":row["TaxableAmount"],
                "CgstAmount":row["CgstAmount"],
                "SgstAmount":row["SgstAmount"],
                "IgstAmount":row["IgstAmount"],
                "CgstRate":row["CgstRate"],
                "SgstRate":row["SgstRate"],
                "IgstRate":row["IgstRate"],
                "InvoiceValue":row["InvoiceValue"],
                "Gstin":row["Gstin"],
                "VehicleNo":row["VehicleNo"],
                "TransporterName":row["TransporterName"],
                "IrnNo":row["IrnNo"]
            }

            arr.append(obj)

        df.apply(uploadData, axis=1)
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        uploadDetails = requests.post(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/createsupplierportalasn", json=arr, headers=headers).json()
        print(uploadDetails['data'])

        responseData = []
        for upload_data in uploadDetails['data']:
            responseData.append({'AsnNo': upload_data['AsnNo'],
                                 'ChallenNo': upload_data['ChallenNo'],
                                 'PoNo': upload_data['PoNo'],
                                 'ChallenDate': upload_data['ChallenDate'],
                                 'ERROR': upload_data['ERROR']
                                 })

        poDetails = requests.get(url=f"http://webapp.webhop.net:8399/api/SupplierPortalApi/getpolist?CompanyId={id}", headers=headers).json()['data']
        return render(request, 'dashboard/dashboard.html', {'po': len(poDetails), 'id': id, 'data': responseData})

    return redirect(f'http://127.0.0.1:8000/company/{id}/', {'data': uploadDetails})
    # return HttpResponse("Success")
