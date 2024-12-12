from typing import Dict, List
import sys


class ProteinParam:
    """
    Calculate various physical and chemical properties of a protein sequence.
    
    Properties calculated include:
    - Molecular weight
    - Absorbance at 280 nm
    - Isoelectric point (pI)
    - Amino acid composition
    - Extinction coefficients
    """
    
    # Amino acid molecular weights
    aa2mw = {
        'A': 89.093,  'G': 75.067,  'M': 149.211, 'S': 105.093, 'C': 121.158,
        'H': 155.155, 'N': 132.118, 'T': 119.119, 'D': 133.103, 'I': 131.173,
        'P': 115.131, 'V': 117.146, 'E': 147.129, 'K': 146.188, 'Q': 146.145,
        'W': 204.225, 'F': 165.189, 'L': 131.173, 'R': 174.201, 'Y': 181.189
    }
    
    # Constants for calculations
    mwH2O = 18.015
    aa2abs280 = {'Y': 1490, 'W': 5500, 'C': 125, 'F': 200}
    aa2chargePos = {'K': 10.5, 'R': 12.4, 'H': 6}
    aa2chargeNeg = {'D': 3.86, 'E': 4.25, 'C': 8.33, 'Y': 10}
    aaNterm = 9.69
    aaCterm = 2.34

    def __init__(self, protein: str):
        """
        Initialize with a protein sequence.
        
        Args:
            protein: Amino acid sequence string
        """
        self.AminoList = list(self.aa2mw.keys())
        self.Chain = protein.upper()
        self.StringLength = len(protein)
        self.AminoCount = None
        self.AADict = None
        # Initialize amino acid counts
        self.aaCount()

    def aaCount(self) -> int:
        """
        Count the number of each amino acid in the sequence.
        
        Returns:
            Total number of amino acids
        """
        self.AminoCount = [self.Chain.count(aa) for aa in self.AminoList]
        self.AADict = dict(zip(self.AminoList, self.AminoCount))
        return sum(self.AminoCount)

    def aaComposition(self) -> Dict[str, int]:
        """
        Get amino acid composition of the sequence.
        
        Returns:
            Dictionary of amino acid counts
        """
        return self.AADict

    def molecularWeight(self) -> float:
        """
        Calculate molecular weight of the protein.
        
        Returns:
            Molecular weight in Daltons
        """
        mol_sum = sum(
            count * (self.aa2mw[aa] - self.mwH2O)
            for aa, count in zip(self.AminoList, self.AminoCount)
        )
        return self.mwH2O + mol_sum

    def molarExtinction(self) -> float:
        """
        Calculate the molar extinction coefficient.
        
        Returns:
            Molar extinction coefficient
        """
        return sum(
            self.AADict[aa] * self.aa2abs280[aa]
            for aa in self.aa2abs280
        )

    def massExtinction(self) -> float:
        """
        Calculate mass extinction coefficient.
        
        Returns:
            Mass extinction coefficient
        """
        mw = self.molecularWeight()
        return self.molarExtinction() / mw if mw else 0.0

    def _charge_(self) -> float:
        """
        Calculate the charge of the protein at different pH values.
        
        Returns:
            pH at which the protein has zero net charge (pI)
        """
        pos_aas = list(self.aa2chargePos.keys())
        neg_aas = list(self.aa2chargeNeg.keys())
        charges = []
        ph_values = []

        for n in range(1400):
            ph = n * 0.01
            
            # Calculate positive charges
            pos_charge = sum(
                self.AADict.get(aa, 0) * (10**self.aa2chargePos[aa]) / 
                (10**self.aa2chargePos[aa] + 10**ph)
                for aa in pos_aas
            )
            # Add N-terminus charge
            pos_charge += (10**self.aaNterm) / (10**self.aaNterm + 10**ph)
            
            # Calculate negative charges
            neg_charge = sum(
                self.AADict.get(aa, 0) * (10**ph) /
                (10**self.aa2chargeNeg[aa] + 10**ph)
                for aa in neg_aas
            )
            # Add C-terminus charge
            neg_charge += (10**ph) / (10**self.aaCterm + 10**ph)
            
            net_charge = abs(pos_charge - neg_charge)
            charges.append(net_charge)
            ph_values.append(ph)

        # Find pH where charge is closest to zero
        min_charge_index = charges.index(min(charges))
        return ph_values[min_charge_index]

    def pI(self) -> float:
        """
        Calculate the isoelectric point.
        
        Returns:
            Isoelectric point (pI)
        """
        return self._charge_()


def main():
    """Main function to run protein parameter calculations interactively."""
    while True:
        inString = input('protein sequence?')
        if not inString:
            break
            
        # Create parameter calculator
        myParamMaker = ProteinParam(inString)
        myAAnumber = myParamMaker.aaCount()
        
        # Print results
        print(f"Number of Amino Acids: {myAAnumber}")
        print(f"Molecular Weight: {myParamMaker.molecularWeight():.1f}")
        print(f"molar Extinction coefficient: {myParamMaker.molarExtinction():.2f}")
        print(f"mass Extinction coefficient: {myParamMaker.massExtinction():.2f}")
        print(f"Theoretical pI: {myParamMaker.pI():.2f}")
        
        # Print amino acid composition
        print("Amino acid composition:")
        myAAcomposition = myParamMaker.aaComposition()
        denominator = myAAnumber if myAAnumber > 0 else 1
        
        for aa in sorted(myAAcomposition.keys()):
            percentage = myAAcomposition[aa] / denominator * 100
            print(f"\t{aa} = {percentage:.2f}%")


if __name__ == "__main__":
    main()