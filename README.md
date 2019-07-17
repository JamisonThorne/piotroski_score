# piotroski_score

I have not tested this program on any OS except Linux Ubuntu

Things to install in order to run:

Install virtualenv:

	pip install virtualenv

Installing git:

	sudo apt-get install git-all

Steps for running this program in Linux Ubunto:

Note: The following program uses Python 3.6.8

Create virtual environment directory:

	virtualenv -p python3 ~/piotroski_env

Activate virtual env:

	source ~/piotroski_env/bin/activate

Create a clone of repository from Github onto computer:

	git clone https://github.com/lastfermat/piotroski_score

Install requirements.txt file in virtual environment:

	pip install -r requirements.txt

You can choose to run this program through the entire stock list which should take around 6 hours or you can run a specified number of rows. No change is needed to run the program all the way through. To run the program through the first, say ten stocks uncomment line 45 and comment line 47.

Run Program:

	python piotroski_score.py

Look at results:

	libreoffice fscore.csv &

Note: This program can be made more efficient by using the morningstar API. For learning purposes, I am using selenium's chromedriver instead.

This is program calculates the F-Score (Piotroski Score) for all active stocks on the AMAX, NASDAQ, and NYSE.

Piotroski's research publication:

https://www.chicagobooth.edu/~/media/FE874EE65F624AAEBD0166B1974FD74D.pdf

PROFITABILITY

F_ROA:
    Purpose: Current Profitability and Cash flow realizations provide information about the firm's ability to generate 
             funds internally. Given the poor historical earnings performance of value firms, 
             any firm currently generating positive cash flow or profits is demonstrating a 
             capacity to generate funds through operating activities.
    
    Definition: ROA is net income before extraordinary items.
    
                F_ROA equals 1 if the firm ROA is positive, 
                zero otherwise.
    
    Morning Star: Key Ratios > Net Income
                  Financials > Balance Sheet > Total Assets
                  
    Equations: Return on Assets = Net Income (This Year) / Total Assets (This Year)

F_DeltaROA:
        Purpose: Current Profitability and Cash flow realizations provide information about the firm's ability to generate 
                 funds internally. Given the poor historical earnings performance of value firms, 
                 any firm currently generating positive cash flow or profits is demonstrating a 
                 capacity to generate funds through operating activities.
        
        Definition: DeltaROA is net income before extraordinary items for this year less the year before.
        
                    F_DeltaROA equals 1 if DeltaROA is positive, otherwise 0.
                    
        Morning Star: Key Ratios > Net Income
                      Financials > Balance Sheet > Total Assets
                      
        Equation: DeltaROA = ROA (This Year) - ROA (Last Year)
F_CFOROA:
    Purpose: Current Profitability and Cash flow realizations provide information about the firm's ability to generate 
             funds internally. Given the poor historical earnings performance of value firms, 
             any firm currently generating positive cash flow or profits is demonstrating a 
             capacity to generate funds through operating activities.
    
    Definition: CFO is cash flow from operations.
    
                F_CFO equals one if CFO is positive, zero otherwise.
    
    Morning Star: Key Ratios > Financials > Operating Cash Flow (USD Mil)
                  Financials > Balance Sheet > Total Assets 

    Equation: CFO = Operating Cash Flow (This Year) / Total Assets (This Year)

F_ACCRUAL:
        Purpose: To include the relationship between earnings and cash flow levels. Earnings 
                 driven by positive acrrual adjustments (profits are greater than cash flow 
                 from operations) is a bad signal about future profitability and returns.
                 
        Defintion: ACCRUAL is the current year's net income before extraordinary items less cash flow from operations, scaled by beginning of the year total assets.

Note: I changed the equation around in my calculation to the equivalent: CFO - NI where:
        
                   F_ACCRUAL equals one if ACCRUAL > 0, zero otherwise.
                   
        Morning Star: Key Ratios > Net Income
                      Key Ratios > Financials > Operating Cash Flow (USD Mil)
        
        Equations: ACCRUAL = CFO (current year) - Net Income (current year)

FUNDING

F_DeltaLever:
            Purpose: By raising external capital, a financially distressed firm is 
                     signaling its inability to generate sufficient internal funds. 
                     In addition, an increase in long-term debt is likely to place 
                     additional constraints on the firm's financial flexbility.
            
            Definition: Captures changes in firm's long-term debt levels.
            
                        F_DeltaLever equals 1 if DeltaLever is positive, else 0.
                        
            Morning Star: Key Ratios > Financial Health Tab > Debt/Equity
                        
            Equations: Leverage or Gearing (debt/equity) = Total Liabilities / Average total assets
                       DeltaLever = Leverage (Last Year) - Leverage (This Year)


F_DeltaLiquid:
            Purpose: Piotroski assumes that an improvement in liquidty is a good 
                     signal about the firm's ability to service current debt obligations
            
            Definition: DeltaLiquid measures the Historical change in the firm's current 
                        ratio between the current and prior year. The current 
                        ratio is the ratio of current assets to current liabilities 
                        at fiscal year-end. 
                        
                        F_DeltaLiquid equals one if the firm's 
                        liquidity improved, zero otherwise.
                        
            Morning Star: Financials > Balance Sheet > Total Current Liabilities
                          Financials > Balance Sheet > Total Current Assets
                
            Equations: Current Ratio = Total Current Assets / Total Current Liabilities
                       DeltaLiquid = Current Ratio (This Year) - Current Ratio (Last Year)


EQ_OFFER:
        Purpose: Similar to an increase in long-term debt, financially distressed 
                  firms that raise external capital could be signaling their inability 
                  to generate sufficient interal funds to service future obligations.
                  
        Defintion: Equal to one if the firm did not issue (or less) common equity in the year 
                   preceding portfolio formation, zero otherwise.
         
         Morning Star: Key Ratios > Shares
     
        Equations: EQ_OFFER = Compare Issued Shares (This Year) to Issued Shares (Last Year)


EFFICIENCY

Note: To go quarterly just pull TTM and the previous year off the key ratios page from morningstar

F_DeltaMargin:
            Purpose: Improvement in margins signifies a potential improvement in factor costs, 
                     a reduction in inventory costs, or a rise in the price of the firm's product.
                     
            Definition: DeltaMargin is the firm's current gross margin ratio (gross margin scaled 
                        by total sales) less the prior year's gross margin ratio.
            
                        F_DeltaMargin equals one if DeltaMargin is positive, zero otherwise.
                        
            Morning Star: Key Ratios > Profitability Tab > Gross Margin
            
            Equations: DeltaMargin = Gross Margin Ratio (This Year) - Gross Margin Ratio (Previous Year)

F_DeltaTurn:
        Purpose: An improvement in asset turnover signifies greater productivity from the 
                 asset base. Such an improvement can arise from more efficient operations 
                 (fewer assets generating the same levels of sales) or an icnrease in sales 
                 (which could also signify improved market conditions for the firm's products).
         
        Defintion: The Firm's current year asset turnover ratio (total sales scaled by beginning 
                   of the year total assets) less the prior year's asset turnover ratio.
        
                   F_DeltaTurn equals one if DeltaTurn is positive, zero otherwise.
                   
        Morning Star: Key Ratios > Efficiency Ratios > Asset Turnover
        
        Equations: Asset Turnover = Revenue / Average Total Assets
                   Average Total Assets = (Total Assets (this year) + Total Assets (previous year)) / 2 
                   DeltaTurn = Asset Turnover (This Year) - Asset Turnover (Last Year)

F_Score = F_ROA + F_DeltaROA + F_CFOROA + F_ACCRUAL + F_DeltaMargin + F_DeltaTurn + F_DeltaLever + F_DeltaLiquid + EQ_OFFER
