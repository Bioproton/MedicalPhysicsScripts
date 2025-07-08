*$ CREATE MGDRAW.FOR
*COPY MGDRAW
*                                                                      *
*=== mgdraw ===========================================================*
*                                                                      *
      SUBROUTINE MGDRAW ( ICODE, MREG )

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1990-2013      by        Alfredo Ferrari           *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     MaGnetic field trajectory DRAWing: actually this entry manages   *
*                                        all trajectory dumping for    *
*                                        drawing                       *
*                                                                      *
*     Created on   01 March 1990   by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*     Last change   12-Nov-13      by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(CASLIM)'
      INCLUDE '(COMPUT)'
      INCLUDE '(SOURCM)'
      INCLUDE '(FHEAVY)'
      INCLUDE '(FLKSTK)'
      INCLUDE '(GENSTK)'
      INCLUDE '(MGDDCM)'
      INCLUDE '(PAPROP)'
      INCLUDE '(QUEMGD)'
      INCLUDE '(SUMCOU)'
      INCLUDE '(TRACKR)'
      INCLUDE '(RESNUC)' 
      INCLUDE '(EVTFLG)'

      INTEGER TrackID
* RESNUC added by Anna
* Integer TrackID added by Sander
* testing   
*
      DIMENSION DTQUEN ( MXTRCK, MAXQMG )
*
      CHARACTER*20 FILNAM
      LOGICAL LFCOPE
      SAVE LFCOPE
      DATA LFCOPE / .FALSE. /
*
*----------------------------------------------------------------------*
*                                                                      *
*     Icode = 1: call from Kaskad                                      *
*     Icode = 2: call from Emfsco                                      *
*     Icode = 3: call from Kasneu                                      *
*     Icode = 4: call from Kashea                                      *
*     Icode = 5: call from Kasoph                                      *
*                                                                      *
*----------------------------------------------------------------------*
*                                                                      *
      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
*  +-------------------------------------------------------------------*
*  |  Quenching is activated
      IF ( LQEMGD ) THEN
         IF ( MTRACK .GT. 0 ) THEN
            RULLL  = ZERZER
            CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*            WRITE (IODRAW) ( ( SNGL (DTQUEN (I,JBK)), I = 1, MTRACK ),
*     &                         JBK = 1, NQEMGD )
         END IF
      END IF
*  |  End of quenching
*     +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     Boundary-(X)crossing DRAWing:                                    *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             19: boundary crossing                                    *
*     Icode = 2x: call from Emfsco                                     *
*             29: boundary crossing                                    *
*     Icode = 3x: call from Kasneu                                     *
*             39: boundary crossing                                    *
*     Icode = 4x: call from Kashea                                     *
*             49: boundary crossing                                    *
*     Icode = 5x: call from Kasoph                                     *
*             59: boundary crossing                                    *
*                                                                      *
*======================================================================*

****************END OF CODE BY ANNA****************************

      ENTRY BXDRAW ( ICODE, MREG, NEWREG, XSCO, YSCO, ZSCO )
      RETURN
*======================================================================*
*                                                                      *
*     Event End DRAWing:                                               *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY EEDRAW ( ICODE )
      RETURN
*
*======================================================================*
*                                                                      *
*     ENergy deposition DRAWing:                                       *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             10: elastic interaction recoil                           *
*             11: inelastic interaction recoil                         *
*             12: stopping particle                                    *
*             13: pseudo-neutron deposition                            *
*             14: escape                                               *
*             15: time kill                                            *
*     Icode = 2x: call from Emfsco                                     *
*             20: local energy deposition (i.e. photoelectric)         *
*             21: below threshold, iarg=1                              *
*             22: below threshold, iarg=2                              *
*             23: escape                                               *
*             24: time kill                                            *
*     Icode = 3x: call from Kasneu                                     *
*             30: target recoil                                        *
*             31: below threshold                                      *
*             32: escape                                               *
*             33: time kill                                            *
*     Icode = 4x: call from Kashea                                     *
*             40: escape                                               *
*             41: time kill                                            *
*             42: delta ray stack overflow                             *
*     Icode = 5x: call from Kasoph                                     *
*             50: optical photon absorption                            *
*             51: escape                                               *
*             52: time kill                                            *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY ENDRAW ( ICODE, MREG, RULL, XSCO, YSCO, ZSCO )

***************START ADDED BY SANDER IN ENDRAW**************************
* The goal of the code here is to estimate the energy deposition in the*
* scintillators. Important steps will be to see if the energy          *
* depositions are at the same coordinates as the interaction           *
* coordinates found in usdraw.                                         *   
    
*     Opening/creating .txt-file for data dumping
      OPEN(UNIT=91, FILE='Energy_deposition.txt', STATUS='UNKNOWN')
*
*     If an FN/PG causes an energy deposition in the scintillator bars
      IF (LLOUSE .EQ. 1 .AND. MREG .GE. 1 .AND. MREG .LE. 48) THEN
*
*      Dump information about the energy deposition
       WRITE(91, '(3I6,1X,3F11.6,1X,4I5,1X,2F11.6)')
     &  NCASE, ICODE, JTRACK,
     &  XSCO, YSCO, ZSCO, ISPUSR(4), ISPUSR(5),
     &  MREG, NP, RULL, ATRACK*1E6


       
      END IF

**************END ADDED BY SANDER IN ENDRAW*****************************

      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
*      WRITE (IODRAW)  0, ICODE, JTRACK, SNGL (ETRACK), SNGL (WTRACK)
*      WRITE (IODRAW)  SNGL (XSCO), SNGL (YSCO), SNGL (ZSCO), SNGL (RULL)
*  +-------------------------------------------------------------------*
*  |  Quenching is activated : calculate quenching factor
*  |  and store quenched energy in DTQUEN(1, jbk)
      IF ( LQEMGD ) THEN
         RULLL = RULL
         CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*         WRITE (IODRAW) ( SNGL (DTQUEN(1, JBK)), JBK = 1, NQEMGD )
      END IF
*  |  end quenching
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     SOurce particle DRAWing:                                         *
*                                                                      *
*======================================================================*
*
      ENTRY SODRAW
      IF ( .NOT. LFCOPE ) THEN

      END IF
*      WRITE (IODRAW) -NCASE, NPFLKA, NSTMAX, SNGL (TKESUM),
*     &                SNGL (WEIPRI)
*  +-------------------------------------------------------------------*
*  |  (Radioactive) isotope: it works only for 1 source particle on
*  |  the stack for the time being
      IF ( ILOFLK (NPFLKA) .GE. 100000 .AND. LRADDC (NPFLKA) ) THEN
         IARES  = MOD ( ILOFLK (NPFLKA), 100000  )  / 100
         IZRES  = MOD ( ILOFLK (NPFLKA), 10000000 ) / 100000
         IISRES = ILOFLK (NPFLKA) / 10000000
         IONID  = ILOFLK (NPFLKA)
*         WRITE (IODRAW) ( IONID,SNGL(-TKEFLK(I)),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: it works only for 1 source particle on
*  |  the stack for the time being
      ELSE IF ( ABS (ILOFLK (NPFLKA)) .GE. 10000 ) THEN
         IONID = ILOFLK (NPFLKA)
         CALL DCDION ( IONID )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: ???
      ELSE IF ( ILOFLK (NPFLKA) .LT. -6 ) THEN
*         WRITE (IODRAW) ( IONID,SNGL(TKEFLK(I)+AMNHEA(-ILOFLK(NPFLKA))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |
      ELSE
*         WRITE (IODRAW) ( ILOFLK(I), SNGL (TKEFLK(I)+AM(ILOFLK(I))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
      END IF
*  |
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     USer dependent DRAWing:                                          *
*                                                                      *
*     Icode = 10x: call from Kaskad                                    *
*             100: elastic   interaction secondaries                   *
*             101: inelastic interaction secondaries                   *
*             102: particle decay  secondaries                         *
*             103: delta ray  generation secondaries                   *
*             104: pair production secondaries                         *
*             105: bremsstrahlung  secondaries                         *
*             110: decay products                                      *
*     Icode = 20x: call from Emfsco                                    *
*             208: bremsstrahlung secondaries                          *
*             210: Moller secondaries                                  *
*             212: Bhabha secondaries                                  *
*             214: in-flight annihilation secondaries                  *
*             215: annihilation at rest   secondaries                  *
*             217: pair production        secondaries                  *
*             219: Compton scattering     secondaries                  *
*             221: photoelectric          secondaries                  *
*             225: Rayleigh scattering    secondaries                  *
*             237: mu pair     production secondaries                  *
*     Icode = 30x: call from Kasneu                                    *
*             300: interaction secondaries                             *
*     Icode = 40x: call from Kashea                                    *
*             400: delta ray  generation secondaries                   *
*  For all interactions secondaries are put on GENSTK common (kp=1,np) *
*  but for KASHEA delta ray generation where only the secondary elec-  *
*  tron is present and stacked on FLKSTK common for kp=npflka          *
*                                                                      *
*======================================================================*
      ENTRY USDRAW ( ICODE, MREG, XSCO, YSCO, ZSCO )

* ****Parameter definitions****                                        *
*                                                                      *
* ICODE = interaction code. Important icodes are 101 for inelastic     *
* interaction, 100 for elastic interaction, 106 for de-excitation, 300 *
* for low energy neutron interaction                                   *
*
* NCASE = history number. For number of primaries = 1000, NCASE will   *
* range from 1 to 1000                                                 *
*
* MREG = current region. Regions values in current NOVO detector model:*
*   1 - 48: Scintillator bars                                          *
*       49: PMMA target                                                *
*       50: Void amongst the scintillator bars                         *
*  51 - 54: Void amongst the electronic boxes                          *
*       55: Void outside the detector                                  *
*       56: Blackbody                                                  *
* 57 - 152: Electric boxes at the ends of each bars                    *
* 153- 200: Air pockets inside electric boxes                          *
*
* JTRACK = id of the current particle being tracked. If jtrack = 1 it  *
* means that the particle that is being tracked is a proton.           *
* The combination JTRACK.EQ.1 and ICODE.EQ.101 means the current       *       
* interaction was inelastic and caused by a proton.    
*
* NP = Number of secondaries. This is specific to the FLUKA stack 
* called GENSTK, which is the stack where secondary particles are being*
* saved. However, information about the residual nucleus is not saved  * 
* in this stack, but in the FLUKA stack named FHEAVY. If one wishes to *
* loop over FHEAVY, one should use NPHEAV instead of NP. See FHEAVY and* 
* GENSTK files for further information.                                *

* Tki(IP) = kinetic energy of the IPth secondary.                      *
* XSCO,YSCO,ZSCO = X,Y,Z coordinate of the interaction                 * 
* Cxr(IP),Cyr(IP),Czr(IP) = x,y,z cosines of the angle the IPth        * 
* particle was emitted with.                                           *


*Use ISPUSR for saving integer values: ICODE, NCASE, JTRACK
*USE SPAUSR for saving floats

***** START ADDED BY SANDER IN USDRAW*****************************
*
*-----------------------INTERACTIONS IN TARGET-------------------------------
      OPEN(UNIT=67, FILE = 'flagged_pgs_fns.txt', STATUS='UNKNOWN')
*
*     If the current region is the target (region 49)
      IF(MREG .EQ. 49) THEN

*       Default flag of true FN/PG is 0 (False)
        LLOUSE = 0
*
*       Reset ParentID and TrackID values for each new NCASE (this part might not work)
        IF (NCASE .EQ. 1 .OR. NCASE .NE. ISPUSR(1)) THEN
*
*        Set ParentID = 0
         ISPUSR(4) = 0
*
*        Set TrackID = 1
         ISPUSR(5) = 1
        END IF
*       
*       Saving information about NCASE (used for TrackID and ParentID purposes)
*       ISPUSR(1) = NCASE
*
*       If current interaction code is 101/106 (PG) or 101 (FN)
        IF(ICODE .EQ. 101 .OR. ICODE .EQ. 106) THEN
*
*        If the incoming particle is a proton (1) or generic heavy ion (-2)
         IF(JTRACK .EQ. 1 .OR. JTRACK .EQ. -2) THEN

*         Looping over all the secondaries created in the interaction.
*         If the number of secondaries are 3, then IP ranges from 1 to 3. 
          DO IP = 1, NP
*
*          If the current secondary is a photon (7)
           IF(KPART(IP) .EQ. 7) THEN
*                 
*           If the current secondary's kinetic energy is greater than 10 keV
            IF(Tki(IP) .GE. 1E-5) THEN

*            Save information about the PG for later use
             ISPUSR(2) = ICODE
             ISPUSR(3) = JTRACK
*           
*            Kinetic energy of the secondary
             SPAUSR(1) = Tki(IP)
*
*            Interaction(source) coordinates
             SPAUSR(2) = XSCO
             SPAUSR(3) = YSCO
             SPAUSR(4) = ZSCO

*            Update TrackID values for PG (ParentID are always 1 for true FN/PG) 
*            !ParentID and TrackID does not work properly!
*
*            ParentID
             ISPUSR(4) = 1
*
*            TrackID
             ISPUSR(5) = 2
             TrackID = ISPUSR(5)
*
*            Flag particle to be a true FN/PG
             LLOUSE = 1
*
             WRITE(67, '(1I6,1X,3I4,1X,4F11.6,1X,1F11.6,1X,2I4)')
     &          NCASE, ICODE, JTRACK, KPART(IP), Tki(IP),
     &          XSCO, YSCO, ZSCO,
     &          ATRACK * 1E6, ISPUSR(4), ISPUSR(5)

            END IF
*
*          If the current secondary is a neutron (8)
           ELSE IF(KPART(IP) .EQ. 8) THEN
*
*           If the secondary's kinetic energy is greater than 100 keV
            IF(Tki(IP) .GE. 1E-4) THEN 

*            Save information about the FN for later use
             ISPUSR(2) = ICODE
             ISPUSR(3) = JTRACK
*
*            Kinetic energy of the secondary
             SPAUSR(1) = Tki(IP)
*
*            Interaction(source) coordinates
             SPAUSR(2) = XSCO
             SPAUSR(3) = YSCO
             SPAUSR(4) = ZSCO

*            Update TrackID values for FN (ParentID are always 1 for true FN/PG)
*            !ParentID and TrackID does not work properly!
*
*            ParentID
             ISPUSR(4) = 1

*            TrackID
             ISPUSR(5) = 2
             TrackID = ISPUSR(5)
*
*            Flag particle to be a true FN/PG
             LLOUSE = 1
*
             WRITE(67, '(1I6,1X,3I4,1X,4F11.6,1X,1F11.6,1X,2I4)')
     &          NCASE, ICODE, JTRACK, KPART(IP), Tki(IP),
     &          XSCO, YSCO, ZSCO,
     &          ATRACK * 1E6, ISPUSR(4), ISPUSR(5)
            END IF
           END IF
          END DO
         END IF
        END IF
      END IF    
*       
*----------------------INTERACTIONS IN THE DETECTOR------------------------------
      OPEN(UNIT=80, FILE = 'FN_PG_detected.txt', STATUS='UNKNOWN')
      OPEN(UNIT=81, FILE = 'non_FN_PG_detected.txt', STATUS='UNKNOWN')
      OPEN(UNIT=82, FILE = 'produced_in_detector.txt', STATUS='UNKNOWN')
*
*     If an interaction happens in the scintillator bars
      IF(MREG .GE. 1 .AND. MREG .LE. 48) THEN
*
*------------------------TRUE FN/PG OUTPUT----------------------------------------
*      If the interaction involves a true FN/PG-particle
       IF (LLOUSE .EQ. 1) THEN
*
*       Update ParentID 
        ISPUSR(4) = ISPUSR(5)
*
*       Loop over all the secondaries created in the interaction.
        DO IP = 1, NP

**        Get A- and Z-values for the interacting nucleus/target particle (NOT USED)
*         CALL USRDCI(ILOFLK(IP),IONA,IONZ, IONM)
*
*        Update TrackID
         TrackID = TrackID + 1
         ISPUSR(5) = TrackID
*         
*        Reassigning KPART(IP) to return something sensible (Carbon-12: -601200 -> -2 (Heavy ion))
         IF(KPART(IP) .LE. -300000) THEN

*         Write output file: 'FN_PG_detected.txt'
          WRITE(80,'(2I5,4I3,1X,2F11.6,1X,6F10.5,1X,2I5,1X,1F11.6)')
     &     NCASE, ICODE, JTRACK, -2, 
     &     ICHTAR, IBTAR, Tki(IP), ETRACK-AM(JTRACK),
     &     XSCO, YSCO, ZSCO, SPAUSR(2), SPAUSR(3), SPAUSR(4),
     &     MREG, LTRACK, ATRACK*1E6
*
         ELSE

*         Write output file: 'FN_PG_detected.txt' 
          WRITE(80,'(2I5,4I3,1X,2F11.6,1X,6F10.5,1X,2I5,1X,1F11.6)')
     &     NCASE, ICODE, JTRACK, KPART(IP), 
     &     ICHTAR, IBTAR, Tki(IP), ETRACK-AM(JTRACK),
     &     XSCO, YSCO, ZSCO, SPAUSR(2), SPAUSR(3), SPAUSR(4),
     &     MREG, LTRACK, ATRACK*1E6
         END IF
*
        END DO
*    
*---------------------NON-TRUE FN/PG OUTPUT-------------------------------------  
*      If the particle interacting in the scintillator is not a true FN/PG
       ELSE IF (LLOUSE .EQ. 0) THEN
*
*       Loop over all the secondaries created in the interaction.
        DO IP = 1, NP
*
**        Get A- and Z-values for the interacting nucleus/target particle (NOT USED)
*         CALL USRDCI(ILOFLK(IP),IONA,IONZ, IONM)
*         
*        Reassigning KPART(IP) to return something sensible (Carbon-12: -601200 -> -2 (Heavy ion))
         IF(KPART(IP) .LE. -300000) THEN
*
*         Write output file: 'non_FN_PG_detected.txt' 
          WRITE(81, '(6I6,1X,5F11.6,1X,2I5,1X,1F11.6)')
     &     NCASE, ICODE, JTRACK, -2, 
     &     ICHTAR, IBTAR, Tki(IP), ETRACK-AM(JTRACK),
     &     XSCO, YSCO, ZSCO,
     &     MREG, LTRACK, ATRACK*1E6
         ELSE

*         Write output file: 'non_FN_PG_detected.txt' 
          WRITE(81, '(6I6,1X,5F11.6,1X,2I5,1X,1F11.6)')
     &     NCASE, ICODE, JTRACK, KPART(IP), 
     &     ICHTAR, IBTAR, Tki(IP), ETRACK-AM(JTRACK),
     &     XSCO, YSCO, ZSCO,
     &     MREG, LTRACK, ATRACK*1E6
         END IF
        END DO
*
       END IF
*
*------------------------------END OF OUTPUT-----------------------------------------
*     If the particle interacts in the void (in case of air), then it is no longer a true FN/PG
      ELSE IF (MREG .GE. 50 .AND. MREG .LE. 55) THEN
       LLOUSE = 0
      END IF

** Updating mother photon energy to any upcoming interactions (daughter photon becomes new mother photon)
*                    IF(KPART(IP) .EQ. 3 .AND. ICODE .EQ. 219) THEN
*                        SPAUSR(1) = Tki(IP - 1)
*                    END IF


** For testing purposes. How many "prompt gammas" are produced in the detector (phantom PGs, ICODE 101 or 106)
*      IF(MREG .EQ. 49) THEN
*       IF(LLOUSE .EQ. 1) THEN
*        DO IP = 1, NP
*         IF(KPART(IP) .EQ. 7) THEN
*            WRITE(82, '(2I7,1X,2I12,1X,1F11.8,1X,3F11.6)')
*     &          NCASE, ICODE, JTRACK, KPART(IP), TKi(IP),
*     &          XSCO, YSCO, ZSCO
*         END IF
*        END DO
*       END IF
*      END IF
*  
* Np = total number of secondaries *
* Kpart (ip) = (Paprop) id of the ip_th secondary *
* Cxr (ip) = x-axis direction cosine of the ip_th secondary *
* Tki (ip) = laboratory kinetic energy of ip_th secondary (GeV)*
* Wei (ip) = statistical weight of the ip_th secondary *
* etc. (look up the full list in $FLUPRO/flukapro/(GENSTK) 

**************************** END ADDED BY SANDER IN USDRAW *************************

      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
* No output by default:
      RETURN
      CLOSE(67)
      CLOSE(80)
      CLOSE(81)
      CLOSE(82)
  
*=== End of subrutine Mgdraw ==========================================*    
      END
